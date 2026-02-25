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