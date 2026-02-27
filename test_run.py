from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from logic.game_engine import GameEngine

class TestGameUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10)
        self.engine = GameEngine() # เรียกใช้คลาสที่ทำเสร็จแล้ว

        self.lbl_time = Label(text="Time: 60", font_size=40)
        self.lbl_score = Label(text="Score: 0", font_size=30)
        self.lbl_question = Label(text="Press 'Start' to play!", font_size=20)
        
        # เพิ่ม Label สำหรับแสดงข้อความเฉลย (สีเหลือง)
        self.lbl_feedback = Label(text="", font_size=25, color=(1, 1, 0, 1))

        # สร้างปุ่มกด
        btn_start = Button(text="Start Game", background_color=(0, 1, 0, 1))
        btn_start.bind(on_press=self.start_test)

        btn_correct = Button(text="Answer CORRECT", background_color=(0, 0, 1, 1))
        btn_correct.bind(on_press=lambda x: self.submit_answer(True))

        btn_wrong = Button(text="Answer WRONG (-5s)", background_color=(1, 0, 0, 1))
        btn_wrong.bind(on_press=lambda x: self.submit_answer(False))

        # จับ Widget ลงหน้าจอ
        self.add_widget(self.lbl_time)
        self.add_widget(self.lbl_score)
        self.add_widget(self.lbl_question)
        self.add_widget(self.lbl_feedback)
        self.add_widget(btn_start)
        self.add_widget(btn_correct)
        self.add_widget(btn_wrong)

        Clock.schedule_interval(self.update_ui, 0.1)

    def start_test(self, instance):
        # จำลองชุดคำถามแบบ Dictionary ให้ตรงกับที่ตกลงกับเพื่อนคนที่ 3 ไว้
        mock_questions = [
            {"question": "ข้อ 1: 1+1 = ?", "answer": "A", "choices": ["A", "B", "C", "D"], "hint": "ง่ายมากๆ"},
            {"question": "ข้อ 2: ภาษาที่ใช้เขียน Kivy คือ?", "answer": "A", "choices": ["A", "B", "C", "D"], "hint": "มีงู"},
            {"question": "ข้อ 3: 2x2 = ?", "answer": "A", "choices": ["A", "B", "C", "D"], "hint": "เลขคู่"}
        ]
        self.engine.set_questions(mock_questions)
        
        self.engine.start_game()
        self.next_question()

    def next_question(self):
        self.lbl_feedback.text = "" # เคลียร์ข้อความเฉลยทิ้ง
        q = self.engine.get_next_question()
        if q:
            # ดึงเฉพาะตัวโจทย์มาแสดง
            self.lbl_question.text = f"Current: {q['question']}"
        else:
            self.lbl_question.text = "Game Over! No more questions."

    def submit_answer(self, is_correct):
        # เช็คว่าติดหน่วงเวลา 3 วิอยู่ไหม
        if not self.engine.is_playing or getattr(self, 'is_waiting', False): 
            return
        
        ans = "A" if is_correct else "B"
        
        # ส่งแค่ ans ไปให้สมองตรวจ (ลบ correct_answer ออกแล้ว)
        check_result = self.engine.check_answer(ans) 
        
        if check_result:
            self.lbl_feedback.text = "ถูกต้อง! 🎉"
            self.next_question() # ไปข้อต่อไปทันที
        else:
            correct_ans = self.engine.current_question.get('answer')
            self.lbl_feedback.text = f"ผิด! หัก 5 วิ (เฉลย: {correct_ans}) รอ 3 วิ..."
            self.is_waiting = True
            
            # สั่งให้รอ 3 วินาทีแล้วค่อยเปลี่ยนข้อ (จำลองจากโค้ดจริงที่คุณทำ)
            Clock.schedule_once(self.delayed_next, 3.0)

    def delayed_next(self, dt):
        """ปลดล็อกและไปข้อต่อไปหลังจากรอครบ 3 วิ"""
        self.is_waiting = False
        if self.engine.is_playing:
            self.next_question()

    def update_ui(self, dt):
        """อัปเดตเวลาและคะแนนแบบ Real-time"""
        self.lbl_time.text = f"Time left: {self.engine.time_left}"
        self.lbl_score.text = f"Score: {self.engine.score}"

class TestApp(App):
    def build(self):
        return TestGameUI()

if __name__ == '__main__':
    TestApp().run()