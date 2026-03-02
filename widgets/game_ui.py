import math
import random

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.animation import Animation

# <--- [เพิ่มส่วนนี้: ตัวแปรสีของสายไฟ] --->
WIRE_COLORS = [
    (1.00, 0.22, 0.18),  # แดง
    (0.18, 0.72, 1.00),  # ฟ้า
    (0.20, 1.00, 0.45),  # เขียว
    (1.00, 0.90, 0.10),  # เหลือง
    (0.85, 0.25, 1.00),  # ม่วง
    (1.00, 0.55, 0.10),  # ส้ม
]
WIRE_COLOR_NAMES = ['🔴 แดง', '🔵 ฟ้า', '🟢 เขียว', '🟡 เหลือง', '🟣 ม่วง', '🟠 ส้ม']
# <--------------------------------->

# ─────────────────────────────────────────────────────────────────────────────
#  VignetteWidget — ไฟแดงกระพริบรอบจอตอนเวลาใกล้หมด
# ─────────────────────────────────────────────────────────────────────────────
class VignetteWidget(Widget):
    vignette_alpha = NumericProperty(0.0)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._draw, size=self._draw, vignette_alpha=self._draw)

    def _draw(self, *_):
        self.canvas.clear()
        if self.vignette_alpha <= 0:
            return
        w, h = self.size
        a = self.vignette_alpha
        with self.canvas:
            thickness = dp(40)
            for step in range(8):
                frac = (8 - step) / 8
                Color(1, 0.05, 0.02, a * frac * 0.18)
                t = thickness * (step / 8)
                Rectangle(pos=(self.x, self.top - t - dp(5)), size=(w, dp(5)))
                Rectangle(pos=(self.x, self.y + t), size=(w, dp(5)))
                Rectangle(pos=(self.x + t, self.y), size=(dp(5), h))
                Rectangle(pos=(self.right - t - dp(5), self.y), size=(dp(5), h))

    def show(self, intensity=1.0):
        self.vignette_alpha = intensity

    def hide(self):
        Animation(vignette_alpha=0, duration=0.3).start(self)

    def pulse_red(self):
        a = (Animation(vignette_alpha=1.0, duration=0.15) +
             Animation(vignette_alpha=0.3, duration=0.15))
        a.start(self)

# ─────────────────────────────────────────────────────────────────────────────
#  ComboDisplay — ข้อความแสดงคอมโบ
# ─────────────────────────────────────────────────────────────────────────────
class ComboDisplay(Label):
    combo = NumericProperty(0)
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_name='Sarabun'
        self.font_size=sp(18)
        self.bold=True
        self.halign='center'
        self.color=(1,0.85,0.1,0)
        self.bind(combo=self._upd)
        
    def _upd(self, *_):
        if self.combo >= 2:
            self.text = f'🔥 COMBO ×{self.combo}!'
            Animation(opacity=1, duration=0.15).start(self)
        else:
            Animation(opacity=0, duration=0.3).start(self)
            
    def flash(self):
        (Animation(font_size=sp(24), duration=0.12) +
         Animation(font_size=sp(18), duration=0.12)).start(self)

# <--- [เพิ่มส่วนนี้: คลาส ClockBombWidget (โครงสร้างพื้นฐาน)] --->
# ─────────────────────────────────────────────────────────────────────────────
#  ClockBombWidget - วิดเจ็ตระเบิดจับเวลาตอนเล่นเกม
# ─────────────────────────────────────────────────────────────────────────────
class ClockBombWidget(Widget):
    wire_states    = ListProperty([])
    correct_wire   = NumericProperty(0)
    num_wires      = NumericProperty(4)
    time_ratio     = NumericProperty(1.0)
    time_display   = StringProperty('10')
    pulse          = NumericProperty(0.0)
    exploding      = BooleanProperty(False)
    explode_t      = NumericProperty(0.0)
    shake_x        = NumericProperty(0.0)
    defused        = BooleanProperty(False)
    digit_scale    = NumericProperty(1.0)
    is_boss        = BooleanProperty(False)
    boss_layer     = NumericProperty(0)   
    wire_order     = ListProperty([])

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(
            pos=self._draw, size=self._draw,
            wire_states=self._draw, pulse=self._draw,
            time_ratio=self._draw, time_display=self._draw,
            exploding=self._draw, explode_t=self._draw,
            shake_x=self._draw, defused=self._draw,
            digit_scale=self._draw, is_boss=self._draw,
            boss_layer=self._draw, wire_order=self._draw,
        )
        self._start_pulse()

    def _start_pulse(self):
        a = (Animation(pulse=1.0, duration=0.5, t='in_out_sine') +
             Animation(pulse=0.0, duration=0.5, t='in_out_sine'))
        a.repeat = True
        a.start(self)

    def reset(self, correct_idx, n_wires, is_boss=False):
        self.num_wires    = n_wires
        self.wire_states  = [-1] * n_wires
        self.correct_wire = correct_idx
        self.exploding    = False
        self.explode_t    = 0.0
        self.shake_x      = 0.0
        self.defused      = False
        self.time_ratio   = 1.0
        self.digit_scale  = 1.0
        self.is_boss      = is_boss
        self.boss_layer   = 0
        self.wire_order   = list(range(n_wires))

    def _draw(self, *_):
        self.canvas.clear()
        w, h = self.size
        if w < 20 or h < 20:
            return
        cx = self.center_x + self.shake_x
        cy = self.y + h * 0.62
        r  = min(w * 0.32, h * 0.40, dp(90))
        with self.canvas:
            self._draw_bomb(cx, cy, r)

    def _draw_bomb(self, cx, cy, r):
        bw, bh = r*2.2, r*1.6
        bx, by = cx-bw/2, cy-bh/2
        
        # วาดบอดี้ระเบิด
        Color(0, 0, 0, 0.40)
        RoundedRectangle(pos=(bx+dp(4), by-dp(4)), size=(bw, bh), radius=[dp(14)])
        Color(0.10, 0.10, 0.14, 1)
        RoundedRectangle(pos=(bx, by), size=(bw, bh), radius=[dp(14)])
        Color(0.18, 0.18, 0.24, 1)
        RoundedRectangle(pos=(bx+dp(2), by+dp(2)), size=(bw-dp(4), bh-dp(4)), radius=[dp(12)])
        
        Color(0.35, 0.35, 0.45, 1)
        Line(rounded_rectangle=(bx, by, bw, bh, dp(14)), width=dp(2.5))
        
        screw_r = dp(5)
        for sx, sy in [(bx+dp(12), by+dp(12)), (bx+bw-dp(12), by+dp(12)),
                       (bx+dp(12), by+bh-dp(12)), (bx+bw-dp(12), by+bh-dp(12))]:
            Color(0.28, 0.28, 0.38, 1)
            Ellipse(pos=(sx-screw_r, sy-screw_r), size=(screw_r*2, screw_r*2))
            Color(0.20, 0.20, 0.28, 1)
            Line(points=[sx-screw_r*.6, sy, sx+screw_r*.6, sy], width=dp(1.2))
            
        # จอ LCD เปล่าๆ
        dw, dh = bw*0.68, bh*0.52
        dx, dy = cx-dw/2, cy-dh/2+bh*0.04
        Color(0.02, 0.10, 0.04, 1)
        RoundedRectangle(pos=(dx, dy), size=(dw, dh), radius=[dp(8)])
        Color(0, 0.12, 0.02, 0.8)
        RoundedRectangle(pos=(dx+dp(2), dy+dp(2)), size=(dw-dp(4), dh-dp(4)), radius=[dp(6)])
        
        t = self.time_ratio
        dr, dg, db = (0.10, 1.00, 0.25) if t > 0.5 else ((1.00, 0.70, 0.05) if t > 0.25 else (1.00, 0.15, 0.05))
        pa = 0.08 + 0.14*self.pulse if t <= 0.25 else 0.04
        Color(dr, dg, db, pa)
        RoundedRectangle(pos=(dx, dy), size=(dw, dh), radius=[dp(8)])
        
        # จุด Colon กะพริบตรงกลางจอ
        ca = 0.5 + 0.5*self.pulse
        Color(dr, dg, db, ca)
        Ellipse(pos=(cx-dp(3), cy+dp(3)), size=(dp(5), dp(5)))
        Ellipse(pos=(cx-dp(3), cy-dp(8)), size=(dp(5), dp(5)))
        
        # ไฟ LED ขวาบน
        led_r = dp(6)
        lx, ly = bx+bw-dp(22), by+bh-dp(15)
        pl = 0.5+0.5*self.pulse if t < 0.5 else 0.4
        Color(1.0, 0.15*(1-t), 0.05, pl)
        Ellipse(pos=(lx-led_r, ly-led_r), size=(led_r*2, led_r*2))
# <------------------------------------------------------------------------>