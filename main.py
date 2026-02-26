from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty
import random

from game_data import category_general, category_it, category_health

all_questions = category_general + category_it + category_health

# --- คลาสสำหรับ Popup แจ้งผล ---
class AnswerPopup(Popup):
    message = StringProperty("")
    color_text = ListProperty([1, 1, 1, 1])

    def __init__(self, is_correct, correct_answer, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback # ฟังก์ชันที่จะให้ทำหลังจากปิด Popup
        
        # จัดการข้อความและสีตามผลลัพธ์
        if is_correct:
            self.title = "ยอดเยี่ยม!"
            self.message = "✅ ถูกต้อง!\nรับไปเลย 1 คะแนน"
            self.color_text = [0.2, 0.9, 0.2, 1] # สีเขียว
        else:
            self.title = "เสียใจด้วย!"
            self.message = f"❌ ผิดครับ!\nคำตอบที่ถูกต้องคือ: {correct_answer}"
            self.color_text = [0.9, 0.2, 0.1, 1] # สีแดง

    def on_dismiss(self):
        # เมื่อ Popup ถูกปิด ให้รันฟังก์ชัน callback (เพื่อสุ่มข้อใหม่ หรือจบเกม)
        self.callback()

# --- คลาสหลักของเกม ---
class GameScreen(Screen):
    def on_pre_enter(self):
        self.score = 0
        self.question_count = 0
        self.max_questions = 10
        self.current_round_questions = random.sample(all_questions, self.max_questions)
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

class ResultScreen(Screen):
    def on_enter(self):
        game_screen = self.manager.get_screen('game')
        real_score = game_screen.score
        total_questions = game_screen.max_questions
        
        self.ids.final_score.text = f"{real_score} / {total_questions}"
        feedback_text = self.get_feedback(real_score, total_questions)
        self.ids.feedback_label.text = feedback_text
        
    def get_feedback(self, score, total_questions):   
        percentage = (score / total_questions) * 100
        if percentage == 100:
            return "อัจฉริยะ! คุณได้คะแนนเต็ม!"
        elif percentage >= 80:
            return "ยอดเยี่ยมมาก! คุณมีความรู้แน่นปึ้ก" 
        elif percentage >= 50:
            return "ผ่านเกณฑ์! พยายามอีกนิดนะ"
        else:
            return "ไม่เป็นไรนะ ลองกลับไปทบทวนดูอีกที!"

class MyGameApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(ResultScreen(name='result'))
        return sm
    
if __name__ == '__main__':
    MyGameApp().run()