from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from logic.game_engine import GameEngine

class TestGameUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10)
        self.engine = GameEngine() # เรียกใช้คลาส

        self.lbl_time = Label(text="Time: 60", font_size=40)
        self.lbl_score = Label(text="Score: 0", font_size=30)
        self.lbl_question = Label(text="Press 'Start' to play!", font_size=20)

        # สร้างปุ่มกด
        btn_start = Button(text="Start Game", background_color=(0, 1, 0, 1))
        btn_start.bind(on_press=self.start_test)

        btn_correct = Button(text="Answer CORRECT", background_color=(0, 0, 1, 1))
        btn_correct.bind(on_press=lambda x: self.submit_answer(True))

        btn_wrong = Button(text="Answer WRONG (-5s)", background_color=(1, 0, 0, 1))
        btn_wrong.bind(on_press=lambda x: self.submit_answer(False))

        self.add_widget(self.lbl_time)
        self.add_widget(self.lbl_score)
        self.add_widget(self.lbl_question)
        self.add_widget(btn_start)
        self.add_widget(btn_correct)
        self.add_widget(btn_wrong)

        Clock.schedule_interval(self.update_ui, 0.1)

    def start_test(self, instance):
        # จำลองชุดคำถาม 5 ข้อ 
        mock_questions = ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]
        self.engine.set_questions(mock_questions)
        
        self.engine.start_game()
        self.next_question()

    def next_question(self):
        q = self.engine.get_next_question()
        if q:
            self.lbl_question.text = f"Current: {q}"
        else:
            self.lbl_question.text = "Game Over! No more questions."

    def submit_answer(self, is_correct):
        if not self.engine.is_playing: return
        
        ans = "A" if is_correct else "B"
        self.engine.check_answer(ans, correct_answer="A")
        self.next_question()

    def update_ui(self, dt):
        self.lbl_time.text = f"Time left: {self.engine.time_left}"
        self.lbl_score.text = f"Score: {self.engine.score}"

class TestApp(App):
    def build(self):
        return TestGameUI()

if __name__ == '__main__':
    TestApp().run()