from datetime import timedelta

from .connection import managed_connection
from .records import ActivityRecord


def _escape_search_text(search_text):
    return (
        search_text
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


def _transaction_activity_query(
    *,
    account_id,
    activity_type,
    posting_status,
    search_text,
    group_id,
    category_id,
    start_date,
    end_date,
):
    query = '''
        SELECT
            transactions.id AS record_id,
            'transaction' AS record_type,
            accounts.name AS account_name,
            category_groups.name AS group_name,
            categories.name AS category_name,
            transactions.amount_centavos AS amount_centavos,
            transactions.date_time AS date_time,
            transactions.notes AS notes,
            category_groups.transaction_type AS activity_type,
            NULL AS source_account_id,
            NULL AS destination_account_id,
            NULL AS source_account_name,
            NULL AS destination_account_name,
            CASE category_groups.transaction_type
                WHEN 'income' THEN 'incoming'
                ELSE 'outgoing'
            END AS direction,
            transactions.posting_status AS posting_status
        FROM transactions
        INNER JOIN accounts
            ON transactions.account_id = accounts.id
        INNER JOIN categories
            ON transactions.category_id = categories.category_id
        INNER JOIN category_groups
            ON categories.group_id = category_groups.group_id
    '''
    conditions = []
    params = []

    if search_text:
        search_pattern = f"%{_escape_search_text(search_text)}%"
        conditions.append(
            '''(
                COALESCE(transactions.notes, '') LIKE ? ESCAPE '\\'
                OR accounts.name LIKE ? ESCAPE '\\'
                OR category_groups.name LIKE ? ESCAPE '\\'
                OR categories.name LIKE ? ESCAPE '\\'
            )'''
        )
        params.extend([search_pattern] * 4)

    if account_id is not None:
        conditions.append("transactions.account_id = ?")
        params.append(account_id)

    if activity_type in {"income", "expense"}:
        conditions.append("category_groups.transaction_type = ?")
        params.append(activity_type)

    if posting_status is not None:
        conditions.append("transactions.posting_status = ?")
        params.append(posting_status)
    elif activity_type in {"income", "expense"}:
        conditions.append("transactions.posting_status = 'posted'")

    if group_id is not None:
        conditions.append("categories.group_id = ?")
        params.append(group_id)

    if category_id is not None:
        conditions.append("transactions.category_id = ?")
        params.append(category_id)

    if start_date is not None:
        conditions.append("transactions.date_time >= ?")
        params.append(f"{start_date.isoformat()} 00:00:00")

    if end_date is not None:
        end_date_exclusive = end_date + timedelta(days=1)
        conditions.append("transactions.date_time < ?")
        params.append(
            f"{end_date_exclusive.isoformat()} 00:00:00"
        )

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    return query, params


def _transfer_activity_query(
    *,
    account_id,
    search_text,
    start_date,
    end_date,
):
    direction_expression = "'neutral'"
    direction_params = []
    if account_id is not None:
        direction_expression = '''
            CASE
                WHEN account_transfers.source_account_id = ?
                    THEN 'outgoing'
                WHEN account_transfers.destination_account_id = ?
                    THEN 'incoming'
                ELSE 'neutral'
            END
        '''
        direction_params.extend((account_id, account_id))

    query = f'''
        SELECT
            account_transfers.id AS record_id,
            'transfer' AS record_type,
            source_accounts.name AS account_name,
            'Account Transfer' AS group_name,
            destination_accounts.name AS category_name,
            account_transfers.amount_centavos AS amount_centavos,
            account_transfers.date_time AS date_time,
            account_transfers.notes AS notes,
            'transfer' AS activity_type,
            account_transfers.source_account_id AS source_account_id,
            account_transfers.destination_account_id
                AS destination_account_id,
            source_accounts.name AS source_account_name,
            destination_accounts.name AS destination_account_name,
            {direction_expression} AS direction,
            'posted' AS posting_status
        FROM account_transfers
        INNER JOIN accounts AS source_accounts
            ON account_transfers.source_account_id = source_accounts.id
        INNER JOIN accounts AS destination_accounts
            ON account_transfers.destination_account_id =
               destination_accounts.id
    '''
    conditions = []
    params = direction_params

    if search_text:
        search_pattern = f"%{_escape_search_text(search_text)}%"
        conditions.append(
            '''(
                COALESCE(account_transfers.notes, '') LIKE ? ESCAPE '\\'
                OR source_accounts.name LIKE ? ESCAPE '\\'
                OR destination_accounts.name LIKE ? ESCAPE '\\'
            )'''
        )
        params.extend([search_pattern] * 3)

    if account_id is not None:
        conditions.append(
            '''(
                account_transfers.source_account_id = ?
                OR account_transfers.destination_account_id = ?
            )'''
        )
        params.extend((account_id, account_id))

    if start_date is not None:
        conditions.append("account_transfers.date_time >= ?")
        params.append(f"{start_date.isoformat()} 00:00:00")

    if end_date is not None:
        end_date_exclusive = end_date + timedelta(days=1)
        conditions.append("account_transfers.date_time < ?")
        params.append(
            f"{end_date_exclusive.isoformat()} 00:00:00"
        )

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    return query, params


def get_activity(
    limit=None,
    account_id=None,
    activity_type=None,
    posting_status=None,
    search_text=None,
    group_id=None,
    category_id=None,
    start_date=None,
    end_date=None,
):
    queries = []
    params = []

    include_transactions = activity_type != "transfer"
    include_transfers = (
        posting_status is None
        and activity_type not in {"income", "expense"}
        and group_id is None
        and category_id is None
    )

    if include_transactions:
        transaction_query, transaction_params = (
            _transaction_activity_query(
                account_id=account_id,
                activity_type=activity_type,
                posting_status=posting_status,
                search_text=search_text,
                group_id=group_id,
                category_id=category_id,
                start_date=start_date,
                end_date=end_date,
            )
        )
        queries.append(transaction_query)
        params.extend(transaction_params)

    if include_transfers:
        transfer_query, transfer_params = _transfer_activity_query(
            account_id=account_id,
            search_text=search_text,
            start_date=start_date,
            end_date=end_date,
        )
        queries.append(transfer_query)
        params.extend(transfer_params)

    if not queries:
        return []

    query = " UNION ALL ".join(queries)
    query += '''
        ORDER BY date_time DESC, record_id DESC, record_type DESC
    '''

    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    with managed_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()

    return [ActivityRecord(*row) for row in rows]
