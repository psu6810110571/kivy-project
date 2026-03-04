from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App
from kivy.animation import Animation
import random
from logic.game_engine import GameEngine 
from widgets.game_ui import ClockBombWidget, WireAnswerButton, WIRE_COLORS

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = GameEngine()
        self.ui_updater = None
        self._shuffle_ev = None
        
        self.wire_buttons = []
        self.correct_wire = 0
        self.is_waiting = False
        self.max_time = 10
        self.q_total = 5
        self.q_num = 0

    def on_enter(self):
        app = App.get_running_app()
        level = getattr(app, '_level', 'easy')
        mode = getattr(app, '_game_mode', 'single')
        
        self.engine.reset_game()
        self.engine.setup_level(level, mode)
        self.max_time = self.engine.time_left
        self.engine.start_game()
        
        self._build_wire_buttons(level)
        
        self._load_question()
        if self.ui_updater: self.ui_updater.cancel()
        self.ui_updater = Clock.schedule_interval(self._tick, 0.1)

    def _build_wire_buttons(self, level):
        wire_count = {'easy': 4, 'medium': 5, 'hard': 6, 'sudden': 5, 'daily': 4}
        n = wire_count.get(level, 4)
        
        container = self.ids.get('wire_btn_container')
        if not container: return
        container.clear_widgets()
        self.wire_buttons = []
        
        for i in range(n):
            btn = WireAnswerButton()
            btn.wire_index = i
            btn.wire_color = list(WIRE_COLORS[i % len(WIRE_COLORS)])
            btn.bind(on_release=lambda b, idx=i: self._on_wire_press(idx))
            container.add_widget(btn)
            self.wire_buttons.append(btn)


    def _load_question(self):
        #ดึงคำถามจากสมองมาโชว์ และซ่อนเฉลยลงในสายไฟ
        if 'feedback_label' in self.ids:
            self.ids.feedback_label.text = '✂ แตะปลายสายที่ตรงกับคำตอบ!'

        q = self.engine.get_next_question()
        if not q:
            self._finish_game()
            return

        # สุ่มเอาคำตอบไปซ่อนในสายไฟ
        choices = list(q.get('choices', []))
        ans_idx = q.get('answer_index', 0)
        correct_text = choices[ans_idx] if ans_idx < len(choices) else choices[0]
        
        while len(choices) < len(self.wire_buttons):
            choices.append(f'— หลอก —')
        random.shuffle(choices)

        for i, btn in enumerate(self.wire_buttons):
            btn.answered = False
            btn.is_correct = False
            btn.text = choices[i] if i < len(choices) else ''
            if btn.text == correct_text:
                self.correct_wire = i

        # รีเซ็ตเวลาและระเบิด
        self.engine.time_left = self.max_time
        if 'bomb_widget' in self.ids:
            self.ids.bomb_widget.reset(self.correct_wire, len(self.wire_buttons))
        if 'question_label' in self.ids:
            self.ids.question_label.text = q.get('question', '')
