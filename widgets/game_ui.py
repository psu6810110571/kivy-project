from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty

# --- คลาสสำหรับ Popup แจ้งผล ---
class AnswerPopup(Popup):
    message = StringProperty("")
    color_text = ListProperty([1, 1, 1, 1])

    def __init__(self, is_correct, correct_answer, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback # ฟังก์ชันที่จะให้ทำหลังจากปิด Popup
        
        # จัดการข้อความและสีตามผลลัพธ์
        if is_correct:
            self.title = "ยอดเยี่ยม!"
            self.message = "✅ ถูกต้อง!\nรับไปเลย 1 คะแนน"
            self.color_text = [0.2, 0.9, 0.2, 1] # สีเขียว
        else:
            self.title = "เสียใจด้วย!"
            self.message = f"❌ ผิดครับ!\nคำตอบที่ถูกต้องคือ: {correct_answer}"
            self.color_text = [0.9, 0.2, 0.1, 1] # สีแดง

    def on_dismiss(self):
        # เมื่อ Popup ถูกปิด ให้รันฟังก์ชัน callback (เพื่อสุ่มข้อใหม่ หรือจบเกม)
        self.callback()