from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
from game_data import category_general

class GameScreen(Screen):
    def show_hint(self):
        print("แสดงคำใบ้สำหรับคำถามนี้")
        real_hint = category_general[0]["hint"]
        self.ids.hint_label.text = f"Hint: {real_hint}"

class ResultScreen(Screen):
    def on_enter(self):
        print("เข้าสู่หน้าสรุปคะแนน")
        
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