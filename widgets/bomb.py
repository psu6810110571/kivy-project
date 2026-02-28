from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.animation import Animation

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