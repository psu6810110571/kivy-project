import os
import unicodedata
# บังคับใช้ SDL2 audio ก่อน import kivy ทุกอย่าง — แก้เสียงไม่ดังบน Windows
os.environ['KIVY_AUDIO'] = 'sdl2'

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.core.text import LabelBase
from kivy.core.audio import SoundLoader
from kivy.animation import Animation

# ── Fix Thai Unicode: NFC normalization ────────────────────────────────────────
# Kivy SDL2 backend ต้องการ NFC normalized string จึงจะ render สระ/วรรณยุกต์ถูกต้อง
from kivy.core.text import Label as CoreLabel
_orig_render = CoreLabel.render

def _patched_render(self, *args, **kwargs):
    if self.text:
        self.text = unicodedata.normalize('NFC', self.text)
    return _orig_render(self, *args, **kwargs)

CoreLabel.render = _patched_render

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

    timer_ratio = NumericProperty(1.0)
    timer_color = ListProperty([0.15, 1.0, 0.28])

    def fade_transition(self):
        return FadeTransition(duration=0.3)

    def build(self):
        return Builder.load_file('ui.kv')

    def on_start(self):
        bgm_path = os.path.join(BASE_DIR, 'assets', 'sounds', 'menu_bgm.mp3')
        self.menu_bgm = SoundLoader.load(bgm_path)
        if self.menu_bgm:
            self.menu_bgm.loop   = True
            self.menu_bgm.volume = 0.5
            self.menu_bgm.play()
            print("[BGM] เล่นเพลง menu แล้ว")
        else:
            print(f"[BGM] โหลดเพลงไม่ได้ ตรวจสอบ path: {bgm_path}")

    def stop_menu_bgm(self):
        if getattr(self, 'menu_bgm', None):
            self.menu_bgm.stop()

    def play_menu_bgm(self):
        if getattr(self, 'menu_bgm', None):
            if self.menu_bgm.state != 'play':
                self.menu_bgm.play()

    def btn_press_anim(self, btn):
        a = (Animation(opacity=0.7, duration=0.08) +
             Animation(opacity=1.0, duration=0.08))
        a.start(btn)

    def btn_anim(self, btn):
        self.btn_press_anim(btn)

    def go_to_category(self, name):
        self.player_name = name.strip() or 'Unknown Agent'
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
            if not getattr(self, '_category', None):
                self._category = 'general'
            self._level = 'sudden'
            self.root.current = 'game'
        elif mode == 'daily':
            if not getattr(self, '_category', None):
                self._category = 'general'
            self._level = 'daily'
            self.root.current = 'game'

    def start_2player(self, p2name):
        self._p2_name = p2name.strip() or 'Player 2'
        print(f"ตั้งชื่อผู้เล่น 2 สำเร็จ: {self._p2_name}")
        if not getattr(self, '_category', None):
            self._category = 'general'
        self._game_mode = '2player'
        self._level = 'medium'
        self.root.current = 'game'

    def start_game(self, level):
        print(f"กำลังเริ่มเกมระดับ: {level}...")
        if not getattr(self, '_category', None):
            self._category = 'general'
        if not getattr(self, '_game_mode', None):
            self._game_mode = 'single'
        self._level = level
        self.stop_menu_bgm()
        self.root.current = 'game'

    def _stop_game_engine(self):
        try:
            gs = self.root.get_screen('game')
            if gs.engine.is_playing:
                gs.engine.stop_game()
            if gs.ui_updater:
                gs.ui_updater.cancel()
                gs.ui_updater = None
            if gs._shuffle_ev:
                gs._shuffle_ev.cancel()
                gs._shuffle_ev = None
        except Exception as e:
            print(f"[WARN] _stop_game_engine: {e}")

    def play_again(self):
        print("เริ่มเล่นใหม่อีกครั้ง!")
        self._stop_game_engine()
        self.root.current = 'category'

    def go_home(self):
        self._stop_game_engine()
        self.play_menu_bgm()
        self.root.current = 'menu'

    def show_leaderboard(self):
        self._lb_prev = self.root.current
        self.root.current = 'leaderboard'

    def go_back_from_lb(self):
        self.root.current = getattr(self, '_lb_prev', 'menu')

    def show_achievements(self):
        self.root.current = 'achievements'

if __name__ == '__main__':
    QuizApp().run()