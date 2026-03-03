from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import random

class GameEngine:
    def __init__(self):
        # 1. ตัวแปรพื้นฐาน
        self.score = 0
        self.time_left = 0
        self.is_playing = False
        self.timer_event = None

        # 2. ข้อมูลคำถาม (รอรับจากเพื่อน)
        self.all_questions = []
        self.current_question = None

        # 3. ตัวแปรระบบใหม่ (Lives & Combo)
        self.lives = 3
        self.combo = 0
        self.max_combo = 0
        self.correct_count = 0

        # 4. ตัวแปรสำหรับโหมดเกมและความยาก
        self.game_mode = 'single' # โหมด: single, 2player, sudden, daily
        self.level_key = 'easy'   # ระดับ: easy, medium, hard
        self.score_multiplier = 1.0

        # 5. ตัวแปรโหมด 2 ผู้เล่น
        self.p1_score = 0
        self.p2_score = 0
        self.current_player = 1 # 1 หรือ 2

        self.hint_used = False 
        self.hint_message = "" # ข้อความคำใบ้ที่จะแสดง
        # self.ajarn_image_source = 'assets/images/ajarn.png'

        self.warning_sound = SoundLoader.load('assets/sounds/warning.wav')
        self.explosion_sound = SoundLoader.load('assets/sounds/explosion.wav')
        self.Duringquiz_sound = SoundLoader.load('assets/sounds/Duringquiz.wav')  
        if self.Duringquiz_sound:
            self.Duringquiz_sound.loop = True  

    def start_game(self):
        # ป้องกันบั๊ก: ถ้ามีนาฬิกาเก่ารันอยู่
        if self.timer_event:
            self.timer_event.cancel()

        self.is_playing = True

        if getattr(self, 'Duringquiz_sound', None):
            self.Duringquiz_sound.play()
        
        print("Game Started!")
        self.timer_event = Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        if self.time_left > 0:
            self.time_left -= 1

        if self.time_left == 10:
                if getattr(self, 'Duringquiz_sound', None): self.Duringquiz_sound.stop()
                if getattr(self, 'warning_sound', None): self.warning_sound.play()
                print("10 seconds left!")
        else:
            self.time_up()

        # ถ้าถูก: คำนวณคะแนนตามโหมด, เพิ่ม Combo
        # ถ้าผิด: หักหัวใจ (Lives), รีเซ็ต Combo
    def check_answer(self, user_answer_index, correct_answer_index):
        if not self.current_question:
            return False
            
        correct_answer_index = self.current_question.get('answer_index', 0)
        
        if user_answer_index == correct_answer_index:
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.correct_count += 1
            
            # คำนวณคะแนนฐาน + โบนัสคอมโบ นำไปคูณกับความยาก
            base_points = 100
            combo_bonus = max(0, self.combo - 1) * 15
            total_points = int((base_points + combo_bonus) * self.score_multiplier)
            
            # บวกคะแนนให้ตรงกับผู้เล่น (โหมด 1 คน หรือ 2 คน)
            if self.game_mode == '2player':
                if self.current_player == 1:
                    self.p1_score += total_points
                else:
                    self.p2_score += total_points
            else:
                self.score += total_points
                
            print(f"Correct! +{total_points} pts | Combo: x{self.combo}")
            return True
            
        else:
            # หักหัวใจ
            self.combo = 0
            self.lives -= 1
            print(f"Wrong! Lives left: {self.lives}")
            
            # ถ้าหัวใจหมด หรือเล่นโหมด Sudden Death (ตอบผิดทีเดียวตาย)
            if self.lives <= 0 or self.game_mode == 'sudden':
                self.game_over()
                
            return False
    
    def time_up(self):
        if not self.is_playing: return
        
        self.combo = 0
        self.lives -= 1
        print(f"Time Up! Lives left: {self.lives}")
        
        if self.lives <= 0 or self.game_mode == 'sudden':
            self.game_over()

    def game_over(self):
        self.is_playing = False
        if self.timer_event:
            self.timer_event.cancel()

        if getattr(self, 'Duringquiz_sound', None): self.Duringquiz_sound.stop()
        if getattr(self, 'warning_sound', None): self.warning_sound.stop()
        if getattr(self, 'Duringquiz_sound', None): self.Duringquiz_sound.play()

        if self.explosion_sound:
            self.explosion_sound.play()
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

        if getattr(self, 'warning_sound', None):
            self.warning_sound.stop()
        if getattr(self, 'Duringquiz_sound', None):
            self.Duringquiz_sound.stop()
        print("Game stop.")

    def get_summary(self):
        summary_data = {
            "mode": self.game_mode,
            "score": self.score,
            "p1_score": self.p1_score,
            "p2_score": self.p2_score,
            "max_combo": self.max_combo,
            "correct_count": self.correct_count,
            "status": "Time Up" if self.lives > 0 else "Finished"
        }
        print(f"Game Summary: {summary_data}")
        return summary_data  
    
    def use_hint(self):
        if self.hint_used or not self.current_question:
            return "ไม่สามารถใช้ตัวช่วยได้!"
            
        self.hint_used = True
        # หักคะแนนแลกกับการใช้ตัวช่วย
        self.score -= 1 
        
        self.hint_message = self.current_question.get('hint', 'ไม่มีคำใบ้สำหรับข้อนี้') 
        print(f"Hint Activated: {self.hint_message}")
        return self.hint_message
    
    def reset_game(self):
        self.stop_game()
        self.score = 0
        self.p1_score = 0
        self.p2_score = 0
        self.current_player = 1
        self.lives = 3
        self.combo = 0
        self.max_combo = 0
        self.correct_count = 0
        self.all_questions = []
        self.current_question = None

        self.hint_used = False
        self.is_playing = False 

        if self.timer_event:
            self.timer_event.cancel()

        if getattr(self, 'warning_sound', None):
            self.warning_sound.stop()

        if getattr(self, 'Duringquiz_sound', None):
            self.Duringquiz_sound.stop()
        print("Game Reset! Ready for new round.")

    def setup_level(self, level_key, mode='single'):
        self.level_key = level_key
        self.game_mode = mode
        
        # ข้อมูลจำลองความยาก 
        levels = {
            'easy':   {'time': 15, 'mult': 1.0},
            'medium': {'time': 10, 'mult': 1.5},
            'hard':   {'time': 7,  'mult': 2.5},
            'sudden': {'time': 8,  'mult': 3.0},
            'daily':  {'time': 10, 'mult': 2.0},
        }
        
        selected = levels.get(level_key, levels['easy'])
        self.time_left = selected['time']
        self.score_multiplier = selected['mult']
        
        print(f"Level Setup: {level_key} mode | Time: {self.time_left}s | Mult: x{self.score_multiplier}")