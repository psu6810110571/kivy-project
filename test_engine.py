from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import random

# ดึงสมองเกม v4.0 ของคุณมาใช้งาน
from logic.game_engine import GameEngine

class TestV4UI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10)
        self.engine = GameEngine()

        # สร้างข้อความแสดงสถานะ
        self.lbl_stats = Label(text="Score: 0 | Lives: 3 | Combo: 0", font_size=25)
        self.lbl_time = Label(text="Time: 0", font_size=35, color=(1, 0.5, 0, 1))
        self.lbl_q = Label(text="Press Start to Play!", font_size=22)
        self.lbl_feedback = Label(text="", font_size=20, color=(1, 1, 0, 1))

        # ปุ่มเริ่มเกม
        btn_start = Button(text="Start Game (Easy Mode)", background_color=(0, 1, 0, 1), size_hint_y=0.5)
        btn_start.bind(on_press=self.start_test)

        self.add_widget(self.lbl_stats)
        self.add_widget(self.lbl_time)
        self.add_widget(self.lbl_q)
        self.add_widget(self.lbl_feedback)
        self.add_widget(btn_start)

        # สร้างปุ่มจำลอง "สายไฟ 4 เส้น" (Index 0, 1, 2, 3)
        self.wire_btns = []
        wire_colors = [(1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1)] # แดง, เขียว, น้ำเงิน, เหลือง
        wire_names = ["ตัดสายที่ 0 (แดง)", "ตัดสายที่ 1 (เขียว)", "ตัดสายที่ 2 (น้ำเงิน)", "ตัดสายที่ 3 (เหลือง)"]
        
        for i in range(4):
            btn = Button(text=wire_names[i], background_color=wire_colors[i])
            # ส่ง Index ของสายไฟ (i) ไปให้ฟังก์ชันตัดสาย
            btn.bind(on_press=lambda instance, idx=i: self.cut_wire(idx)) 
            self.wire_btns.append(btn)
            self.add_widget(btn)

        # ให้อัปเดต UI ทุกๆ 0.1 วินาที
        Clock.schedule_interval(self.update_ui, 0.1)
        self.current_correct_idx = 0 # ตัวแปรเก็บว่าข้อนี้สายไหนคือเฉลย

    def start_test(self, instance):
        # 1. จำลองชุดคำถาม 3 ข้อ
        mock_questions = [
            {"q": "1 + 1 เท่ากับเท่าไหร่?", "correct": 0, "a": ["2", "3", "4", "5"]},
            {"q": "เมืองหลวงของไทยคือ?", "correct": 0, "a": ["กรุงเทพ", "ลอนดอน", "โตเกียว", "ปารีส"]},
            {"q": "สีผสมระหว่างแดงกับน้ำเงินคือ?", "correct": 0, "a": ["ม่วง", "เขียว", "ส้ม", "ดำ"]}
        ]
        
        # 2. โยนคำถามเข้าสมอง และตั้งค่าความยาก (ง่าย = 15 วิ)
        self.engine.set_questions(mock_questions)
        self.engine.setup_level('easy', 'single')
        self.engine.start_game()
        self.next_question()

    def next_question(self):
        q = self.engine.get_next_question()
        if q:
            # จำลองระบบของเพื่อนคนที่ 1: สุ่มว่าเฉลยจะไปอยู่สายไฟเส้นไหน (0 ถึง 3)
            self.current_correct_idx = random.randint(0, 3)
            
            # แอบโชว์เฉลยบนจอเทส จะได้กดถูก
            self.lbl_q.text = f"คำถาม: {q['q']} \n(แอบบอก: ข้อนี้เฉลยอยู่สายที่ {self.current_correct_idx})"
            self.lbl_feedback.text = ""
        else:
            self.lbl_q.text = "คำถามหมดแล้ว! กำลังสรุปผล..."
            self.engine.game_over()
            self.lbl_feedback.text = str(self.engine.get_summary())

    def cut_wire(self, wire_idx):
        if not self.engine.is_playing: return
        
        # ส่ง Index ที่ผู้เล่นกด (wire_idx) กับ Index เฉลย ไปให้สมองตรวจ
        is_correct = self.engine.check_answer(wire_idx, self.current_correct_idx)
        
        if is_correct:
            self.lbl_feedback.text = f"รอดไปได้! 🎉 (Combo x{self.engine.combo})"
            self.next_question()
        else:
            self.lbl_feedback.text = f"ตู้ม! ตัดผิดสาย! โดนหัก 1 หัวใจ 💔"
            # ถ้าหัวใจยังเหลือ ให้โหลดข้อต่อไปมาเล่นต่อ
            if self.engine.lives > 0:
                self.next_question()

    def update_ui(self, dt):
        """อัปเดตตัวเลขหน้าจอให้ตรงกับสมองเกม"""
        self.lbl_time.text = f"Time left: {self.engine.time_left}s"
        self.lbl_stats.text = f"Score: {self.engine.score} | Lives: {self.engine.lives}/3 | Combo: {self.engine.combo}"

class TestApp(App):
    def build(self):
        return TestV4UI()

if __name__ == '__main__':
    TestApp().run()