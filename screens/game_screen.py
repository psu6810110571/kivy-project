from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from logic.game_engine import GameEngine # <--- ดึงสมองเกมที่คุณทำไว้มาใช้งาน

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = GameEngine()
        self.ui_updater = None # ตัวแปรอัปเดตหน้าจอ

    def on_enter(self):
        print("Entered Game Screen!")

        
    def start_game_from_ui(self):
        #ฟังก์ชันสำหรับให้ปุ่ม 'เริ่มเกม' ในหน้าจอ (.kv) เรียกใช้
        self.engine.start_game()
        
        # ให้หน้าจออัปเดตตัวเลขเวลาและคะแนน ทุกๆ 0.1 วินาที
        if self.ui_updater:
            self.ui_updater.cancel()
        self.ui_updater = Clock.schedule_interval(self.update_ui_labels, 0.1)

    def update_ui_labels(self, dt):
        # เช็คว่าเพื่อนคนที่ 1 ตั้งชื่อ id ของ Label ว่าอะไร (สมมติว่าชื่อ time_label กับ score_label)
        if 'time_label' in self.ids:
            self.ids.time_label.text = f"เวลา: {self.engine.time_left}"
        if 'score_label' in self.ids:
            self.ids.score_label.text = f"คะแนน: {self.engine.score}"
            
        # ถ้าเวลาหมด (เกมจบ) ให้หยุดอัปเดตหน้าจอ และบอกให้เปลี่ยนไปหน้าสรุปผล
        if not self.engine.is_playing and self.engine.time_left <= 0:
            if self.ui_updater:
                self.ui_updater.cancel()
            print("หมดเวลา! กำลังส่งข้อมูลไปหน้าสรุปผล...")
            self.manager.current = 'result_screen' # โค้ดสำหรับเปลี่ยนหน้า

    def on_answer_click(self, selected_choice):
        """ฟังก์ชันสำหรับให้ปุ่มตัวเลือก (ก, ข, ค, ง) เรียกใช้เมื่อถูกกด"""
        if not self.engine.is_playing:
            return
            
        is_correct = self.engine.check_answer(selected_choice, correct_answer="A")
        
        if is_correct:
            print("UI ตอบถูก! โหลดคำถามข้อต่อไป...")
            self.engine.get_next_question() # ดึงข้อต่อไปมาแสดงบนจอ

    def load_question_to_ui(self):
        """ดึงคำถามใหม่มาแสดง และเปลี่ยนข้อความบนปุ่ม ก, ข, ค, ง"""
        q_data = self.engine.get_next_question()
        
        if q_data:
            # สมมติเพื่อนคนที่ 1 ตั้ง id ของ Label คำถามว่า 'question_label'
            if 'question_label' in self.ids:
                self.ids.question_label.text = q_data['question']
            
            # สมมติเพื่อนตั้ง id ของปุ่มว่า btn_a, btn_b, btn_c, btn_d
            if 'btn_a' in self.ids:
                self.ids.btn_a.text = q_data['choices'][0]
            if 'btn_b' in self.ids:
                self.ids.btn_b.text = q_data['choices'][1]
            if 'btn_c' in self.ids:
                self.ids.btn_c.text = q_data['choices'][2]
            if 'btn_d' in self.ids:
                self.ids.btn_d.text = q_data['choices'][3]
                
            self.engine.hint_used = False
        else:
            self.finish_game() 

