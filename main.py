from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
import os
import random

# ==========================================
# 🎨 ส่วนที่ 1: Kivy Design (UI & Layouts)
# ==========================================
KV = '''
ScreenManager:
    transition: app.fade_transition()
    MenuScreen:

<MenuScreen>:
    name: 'menu'
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.15, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        spacing: 30
        
        Label:
            text: '[b]TIME-ATTACK QUIZ[/b]\\nSurvive the Bomb!'
            markup: True
            halign: 'center'
            font_size: 45
            color: 1, 0.4, 0.1, 1
            size_hint_y: 0.4
            
        TextInput:
            id: player_name
            hint_text: 'Enter Player Name'
            font_size: 24
            size_hint_y: None
            height: 60
            multiline: False
            halign: 'center'
            
        Button:
            text: 'START MISSION'
            font_size: 30
            size_hint_y: None
            height: 80
            background_color: 0.8, 0.2, 0.2, 1
            background_normal: ''
            bold: True
            on_release: app.go_to_category(player_name.text)
'''

# ==========================================
# 🧠 ส่วนที่ 2: Python Game Logic
# ==========================================
class MenuScreen(Screen):
    pass

class QuizApp(App):
    player_name = StringProperty('Unknown Agent')
    
    def fade_transition(self):
        return FadeTransition(duration=0.3)

    def build(self):
        return Builder.load_string(KV)

    def go_to_category(self, name):
        if name.strip() != '':
            self.player_name = name
        print(f"Agent {self.player_name} is ready!") 

if __name__ == '__main__':
    QuizApp().run()