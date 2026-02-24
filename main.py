from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
from game_data import category_general

class GameScreen(Screen):
    def show_hint(self):
        print("แสดงคำใบ้สำหรับคำถามนี้")
        real_hint = category_general[0]["hint"]
        self.ids.hint_label.text = f"คำใบ้: {real_hint}"

class ResultScreen(Screen):
    def on_enter(self):
        print("เข้าสู่หน้าสรุปคะแนน")
        
        # --- เพิ่ม Logic จำลองคะแนนเพื่อทดสอบหน้า UI ---
        mock_score = 8 
        total_questions = 10
        
        # 1. ส่งคะแนนไปแสดงที่ Label id: final_score
        self.ids.final_score.text = f"คะแนนของคุณคือ: {mock_score} / {total_questions}"
        
        # 2. นำคะแนนไปเข้าฟังก์ชันคำนวณเกรด/คำชม
        feedback_text = self.get_feedback(mock_score, total_questions)
        
        # 3. ส่งคำชมไปแสดงที่ Label id: feedback_label
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