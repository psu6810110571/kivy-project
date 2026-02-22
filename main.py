from kivy.uix.screenmanager import  Screen, ScreenManager
from kivy.app import App

class ResultScreen(Screen):
    def on_enter(self):
        print("เข้าสู่หน้าสรุปคะแนน")

class MyGameApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ResultScreen(name='result'))
        return sm

if __name__ == '__main__':
    MyGameApp().run()