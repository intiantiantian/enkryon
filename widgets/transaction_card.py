from kivymd.uix.card import MDCard

class TransactionCard(MDCard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transaction_id = None

    def set_transaction(self, transaction):
        self.transaction_id = transaction[0]

        self.ids.account_name.text = transaction[1]
        self.ids.group_name.text = transaction[2]
        self.ids.category_name.text = transaction[3]

        amount = transaction[4]

        if transaction[7] == 'income':
            self.ids.amount.text = f"+ ₱{amount}"

        else:
            self.ids.amount.text = f"- ₱{amount}"

        self.ids.date_time.text = transaction[5]
        self.ids.transaction_type.text = transaction[7].upper()

    def edit_transaction(self):
        self.screen.edit_transaction(self.transaction_id)

    def delete_transaction(self):
        self.screen.confirm_delete_transaction(self.transaction_id)