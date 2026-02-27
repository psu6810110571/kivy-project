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

from screens.game_screen import GameScreen
from screens.result_screen import ResultScreen
from widgets.game_ui import AnswerPopup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 1. โหลด Font จากโฟลเดอร์ assets ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LabelBase.register(
    name='Sarabun',
    fn_regular=os.path.join(BASE_DIR, 'assets', 'Sarabun-Regular.ttf'),
    fn_bold   =os.path.join(BASE_DIR, 'assets', 'Sarabun-Bold.ttf'),
)

# ── 2. วิดเจ็ตระเบิด ────────────────────────────────────────────────────────────────
class BombWidget(Widget):
    fuse_opacity = NumericProperty(1.0)
    float_offset = NumericProperty(0.0)
    glow_scale   = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, fuse_opacity=self._draw, float_offset=self._draw, glow_scale=self._draw)
        self._start_animations()

    def _start_animations(self):
        self._float()
        self._spark()
        self._glow()

    def _float(self):
        a = (Animation(float_offset= dp(10), duration=1.4, t='in_out_sine') + Animation(float_offset=-dp(10), duration=1.4, t='in_out_sine'))
        a.repeat = True; a.start(self)

    def _spark(self):
        a = (Animation(fuse_opacity=0.15, duration=0.18) + Animation(fuse_opacity=1.0, duration=0.18) + Animation(fuse_opacity=0.4, duration=0.12) + Animation(fuse_opacity=1.0, duration=0.22))
        a.repeat = True; a.start(self)

    def _glow(self):
        a = (Animation(glow_scale=1.18, duration=0.9, t='in_out_sine') + Animation(glow_scale=0.88, duration=0.9, t='in_out_sine'))
        a.repeat = True; a.start(self)

    def _draw(self, *args):
        self.canvas.clear()
        cx, r = self.center_x, dp(42)
        cy = self.center_y + self.float_offset
        gs, fo = self.glow_scale, self.fuse_opacity
        with self.canvas:
            self._draw_glow(cx, cy, r, gs)
            self._draw_fuse(cx, cy, r)
            self._draw_body(cx, cy, r)
            self._draw_spark(cx, cy, r, fo)

    def _draw_glow(self, cx, cy, r, gs):
        Color(0.9, 0.18, 0.04, 0.10 * gs); Ellipse(pos=(cx - r*gs*1.6, cy - r*gs*1.5), size=(r*gs*3.2, r*gs*3.0))
        Color(0.9, 0.18, 0.04, 0.16 * gs); Ellipse(pos=(cx - r*gs*1.2, cy - r*gs*1.1), size=(r*gs*2.4, r*gs*2.2))

    def _draw_fuse(self, cx, cy, r):
        Color(0.55, 0.42, 0.28, 1); Line(bezier=[cx+r*.36, cy+r*.85, cx+r*.62, cy+r*1.45, cx+r*.26, cy+r*1.80, cx+r*.42, cy+r*2.20], width=dp(2.5))

    def _draw_body(self, cx, cy, r):
        Color(0.13, 0.13, 0.13, 1); Ellipse(pos=(cx-r, cy-r*.92), size=(r*2, r*1.84))
        Color(0.30, 0.30, 0.30, 1); Ellipse(pos=(cx-r*.52, cy+r*.16), size=(r*.62, r*.40))
        Color(1, 0.78, 0.0, 0.80); Line(circle=(cx, cy, r*.86), width=dp(5), dash_offset=8, dash_length=14)
        Color(1, 0.35, 0.0, 1); Ellipse(pos=(cx-dp(5), cy-r*.40), size=(dp(10), dp(10)))
        Rectangle(pos=(cx-dp(4), cy-r*.26), size=(dp(8), dp(22)))

    def _draw_spark(self, cx, cy, r, fo):
        Color(1, 0.90, 0.15, fo); Ellipse(pos=(cx+r*.36, cy+r*2.14), size=(dp(10), dp(10)))
        Color(1, 0.55, 0.05, fo*.65); Ellipse(pos=(cx+r*.28, cy+r*2.06), size=(dp(18), dp(18)))
        Color(1, 0.90, 0.30, fo*.28); Ellipse(pos=(cx+r*.18, cy+r*1.97), size=(dp(28), dp(28)))

# ── 3. หน้าจอต่างๆ ─────────────────────────────────────────────────────────────
class MenuScreen(Screen):
    def on_enter(self):
        title = self.ids.get('title_label')
        if title:
            title.opacity = 0
            Animation(opacity=1, duration=1.0, t='in_cubic').start(title)

class CategoryScreen(Screen):
    pass

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

    def start_game(self, category):
        print(f"กำลังสุ่มคำถามหมวด: {category} ให้กับผู้เล่น {self.player_name}...")
        # 📌 แจ้งเพื่อนคนที่ 2: ให้เขียนโค้ดสลับหน้าจอไปที่ game_screen ตรงนี้นะ!

if __name__ == '__main__':
    QuizApp().run()

