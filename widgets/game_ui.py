import math
import random

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button # <--- [เพิ่มบรรทัดนี้: นำเข้า Button]
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.animation import Animation

WIRE_COLORS = [
    (1.00, 0.22, 0.18),  # แดง
    (0.18, 0.72, 1.00),  # ฟ้า
    (0.20, 1.00, 0.45),  # เขียว
    (1.00, 0.90, 0.10),  # เหลือง
    (0.85, 0.25, 1.00),  # ม่วง
    (1.00, 0.55, 0.10),  # ส้ม
]
WIRE_COLOR_NAMES = ['🔴 แดง', '🔵 ฟ้า', '🟢 เขียว', '🟡 เหลือง', '🟣 ม่วง', '🟠 ส้ม']

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

    def shuffle_wires(self):
        order = list(range(int(self.num_wires)))
        random.shuffle(order)
        self.wire_order = order

    def start_explode(self):
        self.exploding = True
        self.defused   = False
        Animation(explode_t=1.0, duration=0.9, t='out_quad').start(self)

    def start_defuse(self):
        self.defused   = True
        self.exploding = False

    def anim_countdown(self):
        a = (Animation(digit_scale=1.35, duration=0.12, t='out_back') +
             Animation(digit_scale=1.0,  duration=0.12))
        a.start(self)

    def _draw(self, *_):
        self.canvas.clear()
        w, h = self.size
        if w < 20 or h < 20:
            return
        cx = self.center_x + self.shake_x
        cy = self.y + h * 0.62
        r  = min(w * 0.32, h * 0.40, dp(90))
        with self.canvas:
            if self.exploding:
                self._draw_explosion(cx, cy, r)
            elif self.defused:
                self._draw_defused(cx, cy, r)
            else:
                self._draw_bomb(cx, cy, r)
                self._draw_wires(cx, cy, r)

    def _draw_bomb(self, cx, cy, r):
        bw, bh = r*2.2, r*1.6
        bx, by = cx-bw/2, cy-bh/2
        
        if self.is_boss:
            boss_c = 1.0 if self.boss_layer == 0 else 0.6
            Color(1, 0.4*boss_c, 0, 0.25)
            Ellipse(pos=(bx-dp(8), by-dp(8)), size=(bw+dp(16), bh+dp(16)))
            
        Color(0, 0, 0, 0.40)
        RoundedRectangle(pos=(bx+dp(4), by-dp(4)), size=(bw, bh), radius=[dp(14)])
        Color(0.10, 0.10, 0.14, 1)
        RoundedRectangle(pos=(bx, by), size=(bw, bh), radius=[dp(14)])
        Color(0.18, 0.18, 0.24, 1)
        RoundedRectangle(pos=(bx+dp(2), by+dp(2)), size=(bw-dp(4), bh-dp(4)), radius=[dp(12)])
        
        if self.is_boss:
            lc = (1, 0.4, 0.1) if self.boss_layer == 0 else (0.8, 0.2, 1)
            Color(*lc, 0.9)
            Line(rounded_rectangle=(bx, by, bw, bh, dp(14)), width=dp(3.5))
        else:
            Color(0.35, 0.35, 0.45, 1)
            Line(rounded_rectangle=(bx, by, bw, bh, dp(14)), width=dp(2.5))
        
        screw_r = dp(5)
        for sx, sy in [(bx+dp(12), by+dp(12)), (bx+bw-dp(12), by+dp(12)),
                       (bx+dp(12), by+bh-dp(12)), (bx+bw-dp(12), by+bh-dp(12))]:
            Color(0.28, 0.28, 0.38, 1)
            Ellipse(pos=(sx-screw_r, sy-screw_r), size=(screw_r*2, screw_r*2))
            Color(0.20, 0.20, 0.28, 1)
            Line(points=[sx-screw_r*.6, sy, sx+screw_r*.6, sy], width=dp(1.2))
            
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
        
        sc = self.digit_scale
        ddw, ddh = dw*sc, dh*sc
        ddx, ddy = cx-ddw/2, cy-ddh/2+bh*0.04
        self._draw_digits(cx, cy, ddx, ddy, ddw, ddh, dr, dg, db)
        
        ca = 0.5 + 0.5*self.pulse
        Color(dr, dg, db, ca)
        Ellipse(pos=(cx-dp(3), cy+dp(3)), size=(dp(5), dp(5)))
        Ellipse(pos=(cx-dp(3), cy-dp(8)), size=(dp(5), dp(5)))
        
        led_r = dp(6)
        lx, ly = bx+bw-dp(22), by+bh-dp(15)
        pl = 0.5+0.5*self.pulse if t < 0.5 else 0.4
        Color(1.0, 0.15*(1-t), 0.05, pl)
        Ellipse(pos=(lx-led_r, ly-led_r), size=(led_r*2, led_r*2))
        Color(1.0, 0.5, 0.3, pl*0.3)
        Ellipse(pos=(lx-led_r*2, ly-led_r*2), size=(led_r*4, led_r*4))

    def _draw_digits(self, cx, cy, dx, dy, dw, dh, r, g, b):
        try:
            val = int(self.time_display)
        except Exception:
            val = 0
        val = max(0, min(99, val))
        left_x = dx + dw*0.12
        mid_x  = dx + dw*0.54
        Color(r, g, b, 0.90)
        self._draw_7seg(left_x,  dy, dw*0.36, dh, val//10, r, g, b)
        self._draw_7seg(mid_x,   dy, dw*0.36, dh, val%10,  r, g, b)

    def _draw_7seg(self, x, y, w, h, digit, r, g, b):
        sl = w*0.55
        sh = h*0.08
        mx = x+w/2
        ty = y+h*0.84
        my = y+h*0.50
        by_ = y+h*0.14
        
        SEG = {0:[1,1,1,0,1,1,1], 1:[0,0,1,0,0,1,0], 2:[1,0,1,1,1,0,1],
               3:[1,0,1,1,0,1,1], 4:[0,1,1,1,0,1,0], 5:[1,1,0,1,0,1,1],
               6:[1,1,0,1,1,1,1], 7:[1,0,1,0,0,1,0], 8:[1,1,1,1,1,1,1],
               9:[1,1,1,1,0,1,1]}
        segs = SEG.get(digit, [0]*7)
        
        def hs(px, py, on):
            Color(r, g, b, 0.92 if on else 0.08)
            Rectangle(pos=(px-sl/2, py-sh/2), size=(sl, sh))
        def vs(px, py, on):
            Color(r, g, b, 0.92 if on else 0.08)
            Rectangle(pos=(px-sh/2, py-sl*0.5), size=(sh, sl*0.95))
            
        hs(mx, ty,  segs[0])
        vs(mx-sl/2+sh, ty-sl*0.52, segs[1])
        vs(mx+sl/2-sh, ty-sl*0.52, segs[2])
        hs(mx, my,  segs[3])
        vs(mx-sl/2+sh, my-sl*0.52, segs[4])
        vs(mx+sl/2-sh, my-sl*0.52, segs[5])
        hs(mx, by_, segs[6])

    def _draw_wires(self, cx, cy, r):
        bw, bh = r*2.2, r*1.6
        by_ = cy - bh/2
        n   = int(self.num_wires)
        if n == 0:
            return
        spread  = min(bw*0.85, dp(20)*n)
        start_x = cx - spread/2 + spread/(2*n)
        step    = spread/n if n > 1 else 0
        wlen    = dp(72)

        order = list(self.wire_order) if len(self.wire_order) == n else list(range(n))
        for display_pos in range(n):
            real_i = order[display_pos]
            wx    = start_x + display_pos * step
            wt    = by_
            wb    = wt - wlen
            wc    = WIRE_COLORS[real_i % len(WIRE_COLORS)]
            state = self.wire_states[real_i] if real_i < len(self.wire_states) else -1

            if state == 0: 
                mid_y = wt - wlen*0.5
                Color(0.1, 1.0, 0.35, 1)
                Line(points=[wx, wt, wx, mid_y+dp(4)], width=dp(3.5))
                Line(points=[wx, wb, wx, mid_y-dp(4)], width=dp(3.5))
                Color(0.1, 1.0, 0.35, 0.8)
                Ellipse(pos=(wx-dp(7), mid_y-dp(7)), size=(dp(14), dp(14)))
                Color(1, 1, 1, 0.6)
                Ellipse(pos=(wx-dp(3), mid_y-dp(3)), size=(dp(6), dp(6)))
            elif state == 1:
                mid_y = wt - wlen*0.45
                Color(1, 0.2, 0.1, 1)
                Line(points=[wx, wt, wx, mid_y+dp(6)], width=dp(3.5))
                Line(points=[wx, wb, wx, mid_y-dp(6)], width=dp(3.5))
                Color(1, 0.85, 0.1, 0.95)
                Ellipse(pos=(wx-dp(6), mid_y-dp(6)), size=(dp(12), dp(12)))
                Color(1, 0.4, 0.1, 0.5)
                Ellipse(pos=(wx-dp(11), mid_y-dp(11)), size=(dp(22), dp(22)))
            else:
                Color(*wc, 1)
                Line(points=[wx, wt, wx, wb], width=dp(4.5))
                br = dp(14)
                Color(*wc, 0.25)
                Ellipse(pos=(wx-br*1.5, wb-br*1.5), size=(br*3, br*3))
                Color(*wc, 0.85)
                Ellipse(pos=(wx-br, wb-br), size=(br*2, br*2))
                Color(1, 1, 1, 0.30)
                Ellipse(pos=(wx-br*.55, wb+br*.1), size=(br, br*.55))
                Color(*wc, 0.5)
                Line(points=[wx-br*.6, wb, wx+br*.6, wb], width=dp(1.5))

    def _draw_explosion(self, cx, cy, r):
        t = self.explode_t
        Color(1, 0.85, 0.10, max(0, 1.0-t*0.7))
        Ellipse(pos=(cx-r*(1+t*3), cy-r*(1+t*3)), size=(r*2*(1+t*3), r*2*(1+t*3)))
        Color(1, 0.45, 0.02, max(0, 0.85-t))
        Ellipse(pos=(cx-r*(0.6+t*2.2), cy-r*(0.6+t*2.2)), size=(r*2*(0.6+t*2.2), r*2*(0.6+t*2.2)))
        Color(1, 1, 1, max(0, 0.7-t*1.2))
        Ellipse(pos=(cx-r*(0.25+t*.8), cy-r*(0.25+t*.8)), size=(r*2*(0.25+t*.8), r*2*(0.25+t*.8)))
        
        for i in range(16):
            angle = (i/16)*math.pi*2 + t*1.2
            dist  = r*(0.5+t*4.0)
            px    = cx + math.cos(angle)*dist
            py    = cy + math.sin(angle)*dist
            sz    = dp(8)*(1-t*0.8)
            Color(0.15+i*0.02, 0.15, 0.15, max(0, 1-t*1.3))
            Ellipse(pos=(px-sz/2, py-sz/2), size=(sz, sz))
            
        Color(1, 0.65, 0.1, max(0, 0.6-t))
        Line(circle=(cx, cy, r*(0.8+t*5)), width=max(dp(1), dp(4)*(1-t)))

    def _draw_defused(self, cx, cy, r):
        bw, bh = r*2.2, r*1.6
        bx, by = cx-bw/2, cy-bh/2
        
        Color(0.05, 0.18, 0.06, 1)
        RoundedRectangle(pos=(bx, by), size=(bw, bh), radius=[dp(14)])
        Color(0.10, 0.75, 0.25, 0.6)
        Line(rounded_rectangle=(bx, by, bw, bh, dp(14)), width=dp(3))
        
        Color(0.15, 1.0, 0.40, 1)
        ck = r*0.5
        Line(points=[cx-ck*.7, cy, cx-ck*.2, cy-ck*.6, cx+ck*.7, cy+ck*.6],
             width=dp(5), cap='round', joint='round')

    def get_wire_at(self, touch_x, touch_y):
        n = int(self.num_wires)
        if n == 0:
            return -1
        r  = min(self.width*0.32, self.height*0.40, dp(90))
        bw, bh = r*2.2, r*1.6
        cx = self.center_x + self.shake_x
        cy = self.y + self.height*0.62
        by_ = cy - bh/2
        spread  = min(bw*0.85, dp(20)*n)
        start_x = cx - spread/2 + spread/(2*n)
        step    = spread/n if n > 1 else 0
        wlen    = dp(72)
        order   = list(self.wire_order) if len(self.wire_order) == n else list(range(n))
        
        for display_pos in range(n):
            real_i = order[display_pos]
            wx    = start_x + display_pos * step
            wb    = by_ - wlen
            if abs(touch_x-wx) < dp(22) and abs(touch_y-wb) < dp(22):
                return real_i
        return -1

# <--- [เพิ่มโค้ดส่วนนี้: คลาสปุ่มตัวเลือกคำตอบ (WireAnswerButton)] --->
# ─────────────────────────────────────────────────────────────────────────────
#  WireAnswerButton - ปุ่มกดตัวเลือกสายไฟสีต่างๆ
# ─────────────────────────────────────────────────────────────────────────────
class WireAnswerButton(Button):
    wire_index = NumericProperty(0)
    wire_color = ListProperty([1,1,1])
    answered   = BooleanProperty(False)
    is_correct = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_color  = (0,0,0,0)
        self.background_normal = ''
        self.font_name  = 'Sarabun'
        self.font_size  = sp(12)
        self.color      = (1,1,1,1)
        self.halign     = 'center'
        self.valign     = 'middle'
        self.bind(pos=self._r, size=self._r, wire_color=self._r, answered=self._r)

    def _r(self, *_):
        self.canvas.before.clear()
        wc = self.wire_color
        with self.canvas.before:
            if self.answered:
                # ถ้ากดตอบแล้ว ให้เปลี่ยนเป็นสีเขียว(ถูก) หรือ แดง(ผิด)
                c = (0.1,0.9,0.3) if self.is_correct else (1,0.2,0.1)
                Color(*c, 0.35)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
                Color(*c, 1)
            else:
                # สียังไม่กด จะเป็นสีตามสายไฟ
                Color(*wc, 0.20)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
                Color(*wc, 0.85)
            
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)),
                 width=dp(1.8))
            
            if not self.answered:
                Color(*wc, 1)
                dr = dp(4)
                Ellipse(pos=(self.x+dp(7), self.center_y-dr), size=(dr*2, dr*2))
# <----------------------------------------------------------------------->