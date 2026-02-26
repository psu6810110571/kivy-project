from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import random

class GameEngine:
    def __init__(self):
        self.score = 0
        self.time_left = 60
        self.is_playing = False
        self.timer_event = None

        self.all_questions = []
        self.current_question = None

        self.hint_used = False 
        self.hint_message = "" # ข้อความคำใบ้ที่จะแสดง
        # self.ajarn_image_source = 'assets/images/ajarn.png'

        self.warning_sound = SoundLoader.load('assets/sounds/warning.wav')
        self.explosion_sound = SoundLoader.load('assets/sounds/explosion.wav')

    def start_game(self):
        # ป้องกันบั๊ก: ถ้ามีนาฬิกาเก่ารันอยู่
        if self.timer_event:
            self.timer_event.cancel()

        self.score = 0
        self.time_left = 60
        self.is_playing = True
        
        print("Game Started!")
        self.timer_event = Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        if self.time_left > 0:
            self.time_left -= 1
            print(f"Time left: {self.time_left}")
            
            # แจ้งเตือนเวลาใกล้หมด
            if self.time_left == 10:
                print("10 seconds left!")
        else:
            self.game_over()

    def check_answer(self, user_answer, correct_answer):
        if user_answer == correct_answer:
            self.score += 1
            print(f"Correct! Score is now {self.score}")
            return True
        else:
            self.time_left -= 5
            print(f"Wrong! Time penalty -5s. Time left: {self.time_left}")
            return False
        
    def game_over(self):
        self.is_playing = False
        if self.timer_event:
            self.timer_event.cancel()
        print(f"BOOM! Game Over! Final Score: {self.score}")

    def set_questions(self, question_list):
        self.all_questions = question_list.copy()
        random.shuffle(self.all_questions)
        print(f"Loaded {len(self.all_questions)} questions and shuffled!") 

    def get_next_question(self):
        #ดึงคำถามออกมาทีละข้อ (pop)
        if len(self.all_questions) > 0:
            self.current_question = self.all_questions.pop(0)
            return self.current_question
        else:
            print("No more questions!")
            self.game_over()
            return None 

    def stop_game(self):
        self.is_playing = False
        if self.timer_event:
            self.timer_event.cancel()
        print("Game stop.")

    def get_summary(self):
        summary_data = {
            "score": self.score,
            "time_left": self.time_left,
            "status": "Time Up" if self.time_left <= 0 else "Finished"
        }
        print(f"Game Summary: {summary_data}")
        return summary_data  
    
    def use_hint(self):
        if self.hint_used:
            return "ใช้ตัวช่วยไปแล้วครับ!" # ป้องกันไม่ให้กดซ้ำ
            
        self.hint_used = True
        # หักคะแนนแลกกับการใช้ตัวช่วย
        self.score -= 1 
        
        self.hint_message = "อาจารย์บอกว่า: ลองตัดช้อยส์ข้อ ข. ดูสิ!" 
        print(f"Hint Activated: {self.hint_message}")
        return self.hint_message
