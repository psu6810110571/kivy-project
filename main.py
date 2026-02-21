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
            text: 'เกมควิซทะลุเวลา\\n[size=30][color=#ff6666]ตอบให้ไว... ก่อนระเบิดจะทำงาน![/color][/size]'
            markup: True
            font_name: 'Sarabun-Bold.ttf'
            halign: 'center'
            font_size: 60
            color: 1, 0.8, 0.2, 1
            size_hint_y: 0.4
            
        TextInput:
            id: player_name
            hint_text: 'กรอกชื่อสายลับของคุณ...'
            font_name: 'Sarabun-Regular.ttf'
            font_size: 28
            size_hint_y: None
            height: 70
            multiline: False
            halign: 'center'
            padding: [20, 15]
            background_color: 0.9, 0.9, 0.95, 1
            
        # --- [ส่วนที่อัปเดตใน Commit 10] ---
        Button:
            text: 'เริ่มภารกิจ!'
            font_name: 'Sarabun-Bold.ttf'
            font_size: 35
            size_hint_y: None
            height: 80
            background_color: 0, 0, 0, 0  # ทำให้พื้นหลังสี่เหลี่ยมเดิมโปร่งใส
            on_release: app.go_to_category(player_name.text)
            canvas.before:
                Color:
                    rgba: 0.85, 0.2, 0.2, 1  # สีแดงของปุ่ม
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]  # ความโค้งมนของขอบปุ่ม
'''

# ==========================================
# 🧠 ส่วนที่ 2: Python Game Logic
# ==========================================
class MenuScreen(Screen):
    pass

class QuizApp(App):
    player_name = StringProperty('สายลับนิรนาม')  # เปลี่ยนค่าเริ่มต้นเป็นภาษาไทย
    
    def fade_transition(self):
        return FadeTransition(duration=0.3)

    def build(self):
        return Builder.load_string(KV)

    def go_to_category(self, name):
        if name.strip() != '':
            self.player_name = name
        print(f"สายลับ {self.player_name} พร้อมลุย!")  # เปลี่ยนข้อความใน Terminal

if __name__ == '__main__':
    QuizApp().run()