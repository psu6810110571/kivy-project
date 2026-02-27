from kivy.uix.screenmanager import Screen
import random
from data.questions import category_general, category_it, category_health
from widgets.game_ui import AnswerPopup

all_questions = category_general + category_it + category_health

# --- คลาสหลักของเกม ---
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_category = 'all' # สร้างตัวแปรมารับค่าหมวดหมู่

    def on_pre_enter(self):
        self.score = 0
        self.question_count = 0
        self.max_questions = 10
        
        # 1. เช็คว่าผู้เล่นเลือกหมวดไหนมา
        if self.selected_category == 'general':
            question_pool = category_general
        elif self.selected_category == 'it':
            question_pool = category_it
        elif self.selected_category == 'health':
            question_pool = category_health
        else:
            question_pool = all_questions

        # 2. ป้องกัน Error กรณีคำถามในหมวดนั้นมีไม่ถึง 10 ข้อ
        sample_size = min(self.max_questions, len(question_pool))
        self.max_questions = sample_size
        
        self.current_round_questions = random.sample(question_pool, sample_size)
        self.load_random_question()

    def load_random_question(self):
        self.current_question = self.current_round_questions[self.question_count]
        self.ids.question_text.text = self.current_question["question"]
        
        choices = self.current_question["choices"]
        self.ids.btn_choice1.text = choices[0]
        self.ids.btn_choice2.text = choices[1]
        self.ids.btn_choice3.text = choices[2]
        self.ids.btn_choice4.text = choices[3]
        
        self.ids.hint_label.text = ""

    def show_hint(self):
        real_hint = self.current_question["hint"]
        self.ids.hint_label.text = f"คำใบ้: {real_hint}"

    def check_answer(self, selected_choice):
        correct_answer = self.current_question["answer"]
        
        # 1. เช็คว่าตอบถูกหรือผิด
        is_correct = False
        if selected_choice == correct_answer:
            self.score += 1
            is_correct = True
            
        self.question_count += 1
        
        # 2. เปิด Popup แจ้งผล พร้อมส่งฟังก์ชัน next_step ไปให้ทำงานตอนปิด
        popup = AnswerPopup(is_correct, correct_answer, callback=self.next_step)
        popup.open()

    def next_step(self):
        # 3. ฟังก์ชันนี้จะทำงานเมื่อผู้เล่นกดปิด Popup
        if self.question_count >= self.max_questions:
            self.manager.current = 'result'
        else:
            self.load_random_question()