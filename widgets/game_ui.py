from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import NumericProperty
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation

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
            # วาดกรอบสีแดง 4 ด้าน (gradient จากขอบเข้าหากลาง)
            thickness = dp(40)
            for step in range(8):
                frac = (8 - step) / 8
                Color(1, 0.05, 0.02, a * frac * 0.18)
                t = thickness * (step / 8)
                Rectangle(pos=(self.x, self.top - t - dp(5)), size=(w, dp(5)))   # top
                Rectangle(pos=(self.x, self.y + t), size=(w, dp(5)))             # bottom
                Rectangle(pos=(self.x + t, self.y), size=(dp(5), h))             # left
                Rectangle(pos=(self.right - t - dp(5), self.y), size=(dp(5), h)) # right

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