from kivy.app import App
from kivy.uix.label import Label

class MyFinance(App):
    def build(self):
        return Label(text='Welcome to My Finance App!')
    
if __name__ == '__main__':
    MyFinance().run()