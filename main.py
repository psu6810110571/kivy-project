from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
import random

# 1. Import ข้อมูลทั้ง 3 หมวดที่คุณทำไว้
from game_data import category_general, category_it, category_health

# 2. รวมคำถามทั้งหมดเป็นก้อนเดียว (รวม 30 ข้อ)
all_questions = category_general + category_it + category_health

class GameScreen(Screen):
    def on_pre_enter(self):
        # ฟังก์ชันนี้จะทำงานอัตโนมัติ 'ก่อน' ที่หน้าจอจะแสดงผล
        self.load_random_question()

    def load_random_question(self):
        # สุ่มคำถาม 1 ข้อจากทั้งหมดมาเก็บไว้ในตัวแปร current_question
        self.current_question = random.choice(all_questions)
        
        # ส่งข้อความคำถามไปที่ Label
        self.ids.question_text.text = self.current_question["question"]
        
        # ส่งตัวเลือกไปที่ปุ่มทั้ง 4
        choices = self.current_question["choices"]
        self.ids.btn_choice1.text = choices[0]
        self.ids.btn_choice2.text = choices[1]
        self.ids.btn_choice3.text = choices[2]
        self.ids.btn_choice4.text = choices[3]
        
        # เคลียร์คำใบ้เก่าทิ้ง (เผื่อเล่นข้อใหม่)
        self.ids.hint_label.text = ""

    def show_hint(self):
        print("แสดงคำใบ้สำหรับคำถามนี้")
        # ดึงคำใบ้จากข้อที่กำลังเล่นอยู่มาแสดง
        real_hint = self.current_question["hint"]
        self.ids.hint_label.text = f"คำใบ้: {real_hint}"

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