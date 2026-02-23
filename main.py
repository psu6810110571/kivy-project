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

# ── Font ภาษาไทย ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LabelBase.register(
    name='Sarabun',
    fn_regular=os.path.join(BASE_DIR, 'Sarabun-Regular.ttf'),
    fn_bold   =os.path.join(BASE_DIR, 'Sarabun-Bold.ttf'),
)

# ── BombWidget ────────────────────────────────────────────────────────────────
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

# ==========================================
# 🎨 ส่วนที่ 1: Kivy Design
# ==========================================
KV = '''
ScreenManager:
    transition: app.fade_transition()
    MenuScreen:

<MenuScreen>:
    name: 'menu'

    canvas.before:
        Color:
            rgba: 0.03, 0.02, 0.09, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: 0.14, 0.04, 0.28, 0.50
        Ellipse:
            pos: -dp(140), self.height*0.30
            size: dp(460), dp(460)
        Color:
            rgba: 0.40, 0.10, 0.02, 0.38
        Ellipse:
            pos: self.width-dp(220), -dp(100)
            size: dp(400), dp(400)
        Color:
            rgba: 0.16, 0.16, 0.32, 0.28
        Line:
            points: [0, self.height*0.15, self.width, self.height*0.15]
            width: dp(0.6)
        Line:
            points: [0, self.height*0.35, self.width, self.height*0.35]
            width: dp(0.6)
        Line:
            points: [0, self.height*0.55, self.width, self.height*0.55]
            width: dp(0.6)
        Line:
            points: [0, self.height*0.75, self.width, self.height*0.75]
            width: dp(0.6)
        Line:
            points: [0, self.height*0.92, self.width, self.height*0.92]
            width: dp(0.6)
        Line:
            points: [self.width*0.22, 0, self.width*0.22, self.height]
            width: dp(0.6)
        Line:
            points: [self.width*0.50, 0, self.width*0.50, self.height]
            width: dp(0.6)
        Line:
            points: [self.width*0.78, 0, self.width*0.78, self.height]
            width: dp(0.6)
        Color:
            rgba: 1, 0.38, 0.08, 0.13
        Line:
            circle: self.width-dp(50), self.height-dp(50), dp(85)
            width: dp(0.8)
        Color:
            rgba: 1, 0.38, 0.08, 0.06
        Line:
            circle: self.width-dp(50), self.height-dp(50), dp(112)
            width: dp(0.5)
        Color:
            rgba: 0.5, 0.1, 0.9, 0.10
        Line:
            circle: dp(45), dp(45), dp(75)
            width: dp(0.8)

    BoxLayout:
        orientation: 'vertical'
        padding: dp(30), dp(18)
        spacing: dp(0)

        BoxLayout:
            size_hint_y: None
            height: dp(3)
            canvas.before:
                Color:
                    rgba: 1, 0.38, 0.08, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

        Widget:
            size_hint_y: 0.01

        BombWidget:
            size_hint_y: 0.32

        Label:
            id: title_label
            text: '[b]BOMB QUIZ[/b]'
            markup: True
            font_name: 'Sarabun'
            font_size: sp(50)
            color: 1, 0.38, 0.08, 1
            halign: 'center'
            valign: 'middle'
            size_hint_y: None
            height: dp(66)

        BoxLayout:
            size_hint: 0.52, None
            height: dp(2)
            pos_hint: {'center_x': 0.5}
            canvas.before:
                Color:
                    rgba: 1, 0.38, 0.08, 0.80
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: 1, 0.38, 0.08, 0.18
                Rectangle:
                    pos: self.x, self.y-dp(4)
                    size: self.width, dp(10)

        Label:
            text: 'แข่งกับระเบิด  ตอบให้ทัน!'
            font_name: 'Sarabun'
            font_size: sp(17)
            color: 0.68, 0.68, 0.90, 1
            halign: 'center'
            size_hint_y: None
            height: dp(30)

        Widget:
            size_hint_y: 0.05

        BoxLayout:
            size_hint: 0.78, None
            height: dp(24)
            pos_hint: {'center_x': 0.5}
            Label:
                text: 'ชื่อผู้เล่น'
                font_name: 'Sarabun'
                font_size: sp(13)
                color: 1, 0.38, 0.08, 0.9
                halign: 'left'
                valign: 'middle'

        BoxLayout:
            size_hint: 0.78, None
            height: dp(54)
            pos_hint: {'center_x': 0.5}
            padding: dp(2)
            canvas.before:
                Color:
                    rgba: 1, 0.38, 0.08, 0.60
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(12)]
                Color:
                    rgba: 0.06, 0.06, 0.16, 1
                RoundedRectangle:
                    pos: self.x+dp(2), self.y+dp(2)
                    size: self.width-dp(4), self.height-dp(4)
                    radius: [dp(10)]
            TextInput:
                id: player_name
                hint_text: 'พิมพ์ชื่อของคุณที่นี่...'
                font_name: 'Sarabun'
                font_size: sp(18)
                multiline: False
                halign: 'center'
                background_color: 0, 0, 0, 0
                background_normal: ''
                foreground_color: 1, 1, 1, 1
                cursor_color: 1, 0.5, 0.1, 1
                hint_text_color: 0.30, 0.30, 0.50, 1
                padding: dp(12), dp(14)

        Widget:
            size_hint_y: 0.04
            
        # --- [ส่วนที่อัปเดตใน Commit 16: ปุ่ม 3D และส่วนล่าง] ---
        Button:
            id: start_btn
            text: '[b]  เริ่มภารกิจ!  [/b]'
            markup: True
            font_name: 'Sarabun'
            font_size: sp(22)
            size_hint: 0.78, None
            height: dp(62)
            pos_hint: {'center_x': 0.5}
            background_color: 0, 0, 0, 0 
            background_normal: ''
            color: 1, 1, 1, 1
            on_press: app.btn_press_anim(self)
            on_release: app.go_to_category(player_name.text)
            canvas.before:
                # 1. เงาเรืองแสงด้านหลัง (ใหญ่กว่าปุ่มนิดนึง)
                Color:
                    rgba: 0.9, 0.2, 0.05, 0.25
                RoundedRectangle:
                    pos: self.x-dp(4), self.y-dp(4)
                    size: self.width+dp(8), self.height+dp(8)
                    radius: [dp(17)]
                # 2. สีพื้นหลังหลักของปุ่ม
                Color:
                    rgba: 0.85, 0.18, 0.06, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(13)]
                # 3. แสงสะท้อนสีขาวด้านบน (ให้ดูมีมิติ 3D)
                Color:
                    rgba: 1, 1, 1, 0.07
                RoundedRectangle:
                    pos: self.x, self.top-self.height*0.45
                    size: self.width, self.height*0.45
                    radius: [dp(13), dp(13), 0, 0]

        Widget:
            size_hint_y: 0.03

        # version
        Label:
            text: 'TIME-ATTACK QUIZ  v1.0'
            font_name: 'Sarabun'
            font_size: sp(11)
            color: 0.24, 0.24, 0.40, 1
            halign: 'center'
            size_hint_y: None
            height: dp(20)

        Widget:
            size_hint_y: 0.01

        # แถบม่วงล่างสุด
        BoxLayout:
            size_hint_y: None
            height: dp(3)
            canvas.before:
                Color:
                    rgba: 0.45, 0.1, 0.85, 0.75
                Rectangle:
                    pos: self.pos
                    size: self.size
        # --------------------------------------------------------
'''

# ==========================================
# 🧠 ส่วนที่ 2: Python Game Logic
# ==========================================
class MenuScreen(Screen):
    pass

class QuizApp(App):
    player_name = StringProperty('สายลับนิรนาม') 
    
    def fade_transition(self):
        return FadeTransition(duration=0.3)

    def build(self):
        return Builder.load_string(KV)

    # --- [เพิ่มฟังก์ชันอนิเมชันปุ่มตอนกด ใน Commit 16] ---
    def btn_press_anim(self, btn):
        """กระพริบปุ่มตอนกด"""
        a = (Animation(opacity=0.7, duration=0.08) +
             Animation(opacity=1.0, duration=0.08))
        a.start(btn)
    # ------------------------------------------------

    def go_to_category(self, name):
        self.player_name = name.strip() or 'สายลับนิรนาม'
        print(f"Agent '{self.player_name}' is ready!")

if __name__ == '__main__':
    QuizApp().run()