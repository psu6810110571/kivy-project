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