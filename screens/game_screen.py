from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App
from kivy.animation import Animation

from logic.game_engine import GameEngine
from widgets.game_ui import (
    ClockBombWidget, WireAnswerButton,
    VignetteWidget, ComboDisplay,
    WIRE_COLORS, WIRE_COLOR_NAMES
)
import random

class GameScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine        = GameEngine()
        self.ui_updater    = None
        self._shuffle_ev   = None
        self.correct_wire  = 0
        self.wire_buttons  = []
        self.is_waiting    = False
        self.max_time      = 10
        self.q_total       = 5
        self.q_num         = 0