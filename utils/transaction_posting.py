POSTED_STATUS = "posted"
TEMPORARY_STATUS = "temporary"
VALID_POSTING_STATUSES = frozenset(
    {
        POSTED_STATUS,
        TEMPORARY_STATUS,
    }
)


def is_valid_posting_status(posting_status):
    return posting_status in VALID_POSTING_STATUSES
