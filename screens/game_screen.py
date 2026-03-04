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

    # ─── เข้าหน้าจอเกม ──────────────────────────────────────────────────────
    def on_enter(self):
        app    = App.get_running_app()
        level  = getattr(app, '_level',      'easy')
        mode   = getattr(app, '_game_mode',  'single')
        cat    = getattr(app, '_category',   'general')

        # รีเซ็ตเกม
        self.engine.reset_game()
        self.engine.setup_level(level, mode)
        self.max_time = self.engine.time_left
        self.q_num    = 0

        # จำนวนข้อตามความยาก
        q_counts = {'easy': 5, 'medium': 7, 'hard': 10, 'sudden': 30, 'daily': 5}
        self.q_total = q_counts.get(level, 5)

        # โหลดคำถาม
        try:
            from data.questions import get_questions
            questions = get_questions(cat, level)
            self.engine.set_questions(questions)
        except Exception as e:
            print(f"[WARN] questions load error: {e}")
            fallback = [
                {
                    "question": f"คำถามตัวอย่างข้อ {i+1}?",
                    "choices":  ["ตัวเลือก 1", "ตัวเลือก 2", "ตัวเลือก 3", "ตัวเลือก 4"],
                    "answer_index": 0
                }
                for i in range(self.q_total)
            ]
            self.engine.set_questions(fallback)

        # สร้างปุ่มสายไฟ
        self._build_wire_buttons(level)

        # เริ่มเกม
        self.engine.start_game()

        # อัปเดต UI
        if self.ui_updater:
            self.ui_updater.cancel()
        self.ui_updater = Clock.schedule_interval(self._tick, 0.1)

        # โหลดคำถามแรก
        self._load_question()

        # Shuffle สายไฟในโหมด Hard
        if level == 'hard':
            self._shuffle_ev = Clock.schedule_interval(self._shuffle_wires, 2.0)

    def on_leave(self):
        if self.ui_updater:
            self.ui_updater.cancel()
        if self._shuffle_ev:
            self._shuffle_ev.cancel()
        self.wire_buttons = []

    # ─── สร้างปุ่มสายไฟ ──────────────────────────────────────────────────────
    def _build_wire_buttons(self, level):
        wire_count = {'easy': 4, 'medium': 5, 'hard': 6, 'sudden': 5, 'daily': 4}
        n = wire_count.get(level, 4)

        container = self.ids.get('wire_btn_container')
        if not container:
            return
        container.clear_widgets()
        self.wire_buttons = []

        for i in range(n):
            btn = WireAnswerButton()
            btn.wire_index = i
            btn.wire_color = list(WIRE_COLORS[i % len(WIRE_COLORS)])
            btn.text       = ''
            btn.bind(on_release=lambda b, idx=i: self._on_wire_press(idx))
            container.add_widget(btn)
            self.wire_buttons.append(btn)