from kivy.clock import Clock
import random

class GameEngine:
    def __init__(self):
        self.score = 0
        self.time_left = 60  # ให้เวลา 60 วินาที
        self.is_playing = False
        self.timer_event = None