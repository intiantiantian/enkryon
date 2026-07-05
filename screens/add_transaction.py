from kivy.uix.screenmanager import Screen

class AddTransactionScreen(Screen):
    
    def go_to_dashboard(self):
        self.manager.current = 'dashboard'
    
    amount = '0'

    def press_number(self, number):
        if self.amount == '0':
            self.amount = str(number)
        else:
            self.amount += str(number)
        self.update_amount_label()

    def add_decimal(self):
        if '.' not in self.amount:
            self.amount += '.'
        self.update_amount_label()
    
    def delete_last(self):
        if len(self.amount) > 1:
            self.amount = self.amount[:-1]
        else:
            self.amount = '0'
        self.update_amount_label()
    
    def clear(self):
        self.amount = '0'
        self.update_amount_label()

    def update_amount_label(self):
        self.ids.amount_label.text = f'₱ {self.amount}'