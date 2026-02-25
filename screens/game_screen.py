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
            # self.manager.current = 'result_screen' # โค้ดสำหรับเปลี่ยนหน้า
