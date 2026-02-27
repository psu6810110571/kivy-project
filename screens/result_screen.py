from kivy.uix.screenmanager import Screen

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