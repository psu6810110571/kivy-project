from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.widget import Widget
from kivy.core.text import LabelBase
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.animation import Animation
import os

# ── 1. โหลด Font จากโฟลเดอร์ assets ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LabelBase.register(
    name='Sarabun',
    fn_regular=os.path.join(BASE_DIR, 'assets', 'Sarabun-Regular.ttf'),
    fn_bold   =os.path.join(BASE_DIR, 'assets', 'Sarabun-Bold.ttf'),
)

# ── 2. ดึงวิดเจ็ตระเบิดมาจากโฟลเดอร์ widgets ─────────────────────────────────────────
from widgets.bomb import BombWidget

# ── 3. หน้าจอต่างๆ ─────────────────────────────────────────────────────────────
class MenuScreen(Screen):
    def on_enter(self):
        title = self.ids.get('title_label')
        if title:
            title.opacity = 0
            Animation(opacity=1, duration=1.0, t='in_cubic').start(title)

class BriefingScreen(Screen):    
    pass                         

class CategoryScreen(Screen):
    pass

class ModeScreen(Screen):
    pass

class LevelScreen(Screen):
    pass

# <--- [เพิ่มตรงนี้: สร้างคลาสหน้าจอ ResultScreen] --->
class ResultScreen(Screen):
    pass
# <------------------------------------------------>

# ── 4. ตัวควบคุมแอปหลัก ─────────────────────────────────────────────────────────────
class QuizApp(App):
    player_name = StringProperty('Unknown Agent')

    def fade_transition(self):
        return FadeTransition(duration=0.3)

    def build(self):
        # โหลดหน้าตาจากไฟล์ quiz.kv 
        return Builder.load_file('quiz.kv')

    def btn_press_anim(self, btn):
        a = (Animation(opacity=0.7, duration=0.08) +
             Animation(opacity=1.0, duration=0.08))
        a.start(btn)

    def go_to_category(self, name):
        self.player_name = name.strip() or 'Unknown Agent'
        print(f"Agent '{self.player_name}' is ready!")
        self.root.current = 'category'

    def select_category(self, category):
        print(f"หมวดหมู่ที่เลือก: {category}")
        self._category = category
        self.root.current = 'mode'
    
    def set_mode(self, mode):
        print(f"โหมดที่เลือก: {mode}")
        self._game_mode = mode
        if mode == 'single':
            self.root.current = 'level'
        else:
            print(f"กำลังเริ่มเกมโหมดพิเศษ: {mode}")

    def start_game(self, category):
        print(f"กำลังสุ่มคำถามหมวด: {category} ให้กับผู้เล่น {self.player_name}...")
        # 📌 แจ้งเพื่อนคนที่ 2: ให้เขียนโค้ดสลับหน้าจอไปที่ game_screen ตรงนี้นะ!

    # <--- [เพิ่มตรงนี้: ฟังก์ชันชั่วคราวสำหรับปุ่มในหน้า Result] --->
    def play_again(self):
        print("เริ่มเล่นใหม่อีกครั้ง!")
        self.root.current = 'category'

    def go_home(self):
        self.root.current = 'menu'
    # <------------------------------------------------------->

if __name__ == '__main__':
    QuizApp().run()