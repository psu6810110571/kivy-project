from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
import random

# 1. Import ข้อมูลทั้ง 3 หมวดที่คุณทำไว้
from game_data import category_general, category_it, category_health

# 2. รวมคำถามทั้งหมดเป็นก้อนเดียว (รวม 30 ข้อ)
all_questions = category_general + category_it + category_health

class GameScreen(Screen):
    def on_pre_enter(self):
        self.load_random_question()

    def load_random_question(self):
        self.current_question = random.choice(all_questions)
        self.ids.question_text.text = self.current_question["question"]
        
        choices = self.current_question["choices"]
        self.ids.btn_choice1.text = choices[0]
        self.ids.btn_choice2.text = choices[1]
        self.ids.btn_choice3.text = choices[2]
        self.ids.btn_choice4.text = choices[3]
        
        self.ids.hint_label.text = ""

    def show_hint(self):
        print("แสดงคำใบ้สำหรับคำถามนี้")
        real_hint = self.current_question["hint"]
        self.ids.hint_label.text = f"คำใบ้: {real_hint}"

    # --- ฟังก์ชันใหม่: ตรวจคำตอบ ---
    def check_answer(self, selected_choice):
        correct_answer = self.current_question["answer"]
        
        # เช็คว่าข้อความบนปุ่มที่กด ตรงกับ "answer" ในฐานข้อมูลไหม
        if selected_choice == correct_answer:
            print(f"✅ ถูกต้อง! (คุณตอบ: {selected_choice})")
        else:
            print(f"❌ ผิดครับ! (คุณตอบ: {selected_choice} | คำตอบที่ถูกคือ: {correct_answer})")
            
        # ตอบเสร็จปุ๊บ สุ่มข้อใหม่ขึ้นมาแทนที่ทันที
        self.load_random_question()

class ResultScreen(Screen):
    def on_enter(self):
        print("เข้าสู่หน้าสรุปคะแนน")
        mock_score = 8 
        total_questions = 10
        self.ids.final_score.text = f"คะแนนของคุณคือ: {mock_score} / {total_questions}"
        feedback_text = self.get_feedback(mock_score, total_questions)
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