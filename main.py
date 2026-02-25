from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
import random

from game_data import category_general, category_it, category_health

all_questions = category_general + category_it + category_health

class GameScreen(Screen):
    def on_pre_enter(self):
        # 1. รีเซ็ตคะแนนและจำนวนข้อทุกครั้งที่เริ่มเกมใหม่
        self.score = 0
        self.question_count = 0
        self.max_questions = 10  # เล่นรอบละ 10 ข้อ
        
        # 2. สุ่มดึงคำถามมา 10 ข้อจากฐานข้อมูล เพื่อไม่ให้คำถามซ้ำกันใน 1 รอบ
        self.current_round_questions = random.sample(all_questions, self.max_questions)
        
        self.load_random_question()

    def load_random_question(self):
        # ดึงคำถามตามลำดับข้อปัจจุบัน (0 ถึง 9)
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
        
        # 3. ตรวจคำตอบและนับคะแนน
        if selected_choice == correct_answer:
            print(f"✅ ถูกต้อง! ได้ 1 คะแนน")
            self.score += 1  # ตอบถูกบวก 1 คะแนน
        else:
            print(f"❌ ผิดครับ! (คำตอบที่ถูกคือ: {correct_answer})")
            
        self.question_count += 1  # นับว่าเล่นไปแล้ว 1 ข้อ
        
        # 4. เช็คว่าเล่นครบ 10 ข้อหรือยัง
        if self.question_count >= self.max_questions:
            print(f"จบเกม! คะแนนรวม: {self.score}/{self.max_questions}")
            self.manager.current = 'result' # เด้งไปหน้าสรุปผล
        else:
            self.load_random_question() # ยังไม่ครบ โหลดข้อต่อไป

class ResultScreen(Screen):
    def on_enter(self):
        # 5. ดึงคะแนนจริงๆ จากหน้า GameScreen มาใช้งาน
        game_screen = self.manager.get_screen('game')
        real_score = game_screen.score
        total_questions = game_screen.max_questions
        
        # โชว์คะแนนจริง
        self.ids.final_score.text = f"คะแนนของคุณคือ: {real_score} / {total_questions}"
        
        # โชว์คำชมที่คำนวณจากคะแนนจริง
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