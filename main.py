import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.core.text import LabelBase
from kivy.animation import Animation
# ── นำเข้า Widgets และ Screens ─────────────────────────────────────────────────
from widgets.bomb import BombWidget
from widgets.game_ui import VignetteWidget, ComboDisplay, ClockBombWidget, WireAnswerButton
from screens.game_screen import GameScreen

# ── โหลด Font จากโฟลเดอร์ assets ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    LabelBase.register(
        name='Sarabun',
        fn_regular=os.path.join(BASE_DIR, 'assets', 'Sarabun-Regular.ttf'),
        fn_bold   =os.path.join(BASE_DIR, 'assets', 'Sarabun-Bold.ttf'),
    )
except Exception:
    pass

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

class Player2SetupScreen(Screen):
    pass

class ResultScreen(Screen):
    pass

class LeaderboardScreen(Screen):
    def on_enter(self):
        try:
            from data.leaderboard_mgr import populate_leaderboard
            populate_leaderboard(self.ids.lb_grid)
        except Exception as e:
            print(f"[LB] on_enter error: {e}")

class AchievementScreen(Screen):
    def on_enter(self):
        try:
            from data.leaderboard_mgr import populate_achievements
            populate_achievements(self.ids.ach_grid)
        except Exception as e:
            print(f"[ACH] on_enter error: {e}")

# ── ตัวควบคุมแอปหลัก ─────────────────────────────────────────────────────────────
class QuizApp(App):
    player_name = StringProperty('Unknown Agent')
    
    # [สำคัญ] เพิ่มตัวแปรเหล่านี้เพื่อให้ ui.kv ดึงไปใช้วาดแถบเวลาได้โดยไม่ Error
    timer_ratio = NumericProperty(1.0)
    timer_color = ListProperty([0.15, 1.0, 0.28])

    def fade_transition(self):
        return FadeTransition(duration=0.3)

    def build(self):
        # บังคับโหลดไฟล์ ui.kv ตรงๆ แค่รอบเดียวจบ ป้องกันบัคซ้อนกันและบัคจอดำ!
        return Builder.load_file('ui.kv')

    def btn_press_anim(self, btn):
        a = (Animation(opacity=0.7, duration=0.08) +
             Animation(opacity=1.0, duration=0.08))
        a.start(btn)
        
    # เผื่อในไฟล์ .kv มีบางปุ่มใช้ on_press: app.btn_anim(self)
    def btn_anim(self, btn):
        self.btn_press_anim(btn)

    def go_to_category(self, name):
        self.player_name = name.strip() or 'Unknown Agent'
        # อัปเดตชื่อ Agent ใน BriefingScreen
        try:
            briefing = self.root.get_screen('briefing')
            briefing.ids.lbl_agent_name.text = f'AGENT: {self.player_name}'
        except Exception:
            pass
        self.root.current = 'briefing'

    def select_category(self, category):
        print(f"หมวดหมู่ที่เลือก: {category}")
        self._category = category
        self.root.current = 'mode'

    def set_mode(self, mode):
        print(f"โหมดที่เลือก: {mode}")
        self._game_mode = mode
        if mode == 'single':
            self.root.current = 'level'
        elif mode == '2player':
            self.root.current = 'p2setup'
        elif mode == 'sudden':
            self._level = 'sudden'
            self.root.current = 'game'
        elif mode == 'daily':
            self._level = 'daily'
            self.root.current = 'game'