import os
import random

from kivy.clock import Clock
from kivy.core.audio import SoundLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_sound(rel_path):
    full = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(full):
        print(f"[SOUND] ไม่พบไฟล์: {full}")
        return None
    snd = SoundLoader.load(full)
    if snd:
        print(f"[SOUND] โหลดสำเร็จ: {rel_path} (provider={snd.__class__.__name__})")
    else:
        print(f"[SOUND] โหลดไม่ได้: {full}")
    return snd


class GameEngine:
    def __init__(self):
        self.score       = 0
        self.time_left   = 0
        self.is_playing  = False
        self.timer_event = None

        self.all_questions    = []
        self.current_question = None

        self.lives         = 3
        self.combo         = 0
        self.max_combo     = 0
        self.correct_count = 0

        self.game_mode        = 'single'
        self.level_key        = 'easy'
        self.score_multiplier = 1.0

        self.p1_score       = 0
        self.p2_score       = 0
        self.current_player = 1

        self.hint_used    = False
        self.hint_message = ''

        self._reload_sounds()

    # ── เสียง ─────────────────────────────────────────────────────────────────

    def _reload_sounds(self):
        """โหลด sound object ใหม่ทุกรอบ — SDL2 บน Windows ต้องทำแบบนี้"""
        self.Duringquiz_sound = _load_sound('assets/sounds/Duringquiz.wav')
        self.warning_sound    = _load_sound('assets/sounds/warning.wav')
        self.explosion_sound  = _load_sound('assets/sounds/explosion.wav')

        if self.Duringquiz_sound:
            self.Duringquiz_sound.loop   = True
            self.Duringquiz_sound.volume = 1.0
        if self.warning_sound:
            self.warning_sound.volume = 1.0
        if self.explosion_sound:
            self.explosion_sound.volume = 1.0

    def _play(self, snd):
        try:
            if snd:
                snd.volume = 1.0
                snd.play()
        except Exception as e:
            print(f"[SOUND] play error: {e}")

    def _stop(self, snd):
        try:
            if snd:
                snd.stop()
        except Exception as e:
            print(f"[SOUND] stop error: {e}")

    def play_explosion(self):
        """เรียกจากภายนอก (game_screen) เพื่อเล่นเสียงระเบิด"""
        self._stop(self.Duringquiz_sound)
        self._stop(self.warning_sound)
        self._play(self.explosion_sound)

    # ── เริ่มเกม ──────────────────────────────────────────────────────────────

    def start_game(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

        self.is_playing = True
        self._play(self.Duringquiz_sound)
        print("Game Started!")
        self.timer_event = Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        if not self.is_playing:
            return
        if self.time_left > 0:
            self.time_left -= 1
            if self.time_left == 5:
                self._stop(self.Duringquiz_sound)
                self._play(self.warning_sound)

    # ── ตรวจคำตอบ (ใช้ใน test_engine.py) ────────────────────────────────────

    def check_answer(self, user_answer_index, correct_answer_index):
        if not self.current_question:
            return False
        correct_answer_index = self.current_question.get('answer_index', 0)
        if user_answer_index == correct_answer_index:
            self.combo         += 1
            self.max_combo      = max(self.max_combo, self.combo)
            self.correct_count += 1
            base_points  = 100
            combo_bonus  = max(0, self.combo - 1) * 15
            total_points = int((base_points + combo_bonus) * self.score_multiplier)
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
            self.combo  = 0
            self.lives -= 1
            print(f"Wrong! Lives left: {self.lives}")
            if self.lives <= 0 or self.game_mode == 'sudden':
                self.game_over()
            return False

    def time_up(self):
        if not self.is_playing:
            return
        self.combo  = 0
        self.lives -= 1
        print(f"Time Up! Lives left: {self.lives}")
        if self.lives <= 0 or self.game_mode == 'sudden':
            self.game_over()

    # ── จบเกม ─────────────────────────────────────────────────────────────────

    def game_over(self):
        self.is_playing = False
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        self._stop(self.Duringquiz_sound)
        self._stop(self.warning_sound)
        # หมายเหตุ: เสียงระเบิดตอน game_over จะถูกเล่นโดย game_screen
        # เพื่อให้ sync กับ animation ระเบิดบนหน้าจอ
        print(f"BOOM! Game Over! Final Score: {self.score}")

    # ── คำถาม ─────────────────────────────────────────────────────────────────

    def set_questions(self, question_list):
        self.all_questions = question_list.copy()
        random.shuffle(self.all_questions)
        print(f"Loaded {len(self.all_questions)} questions and shuffled!")

    def get_next_question(self):
        if len(self.all_questions) > 0:
            self.current_question = self.all_questions.pop(0)
            return self.current_question
        else:
            print("No more questions!")
            self.game_over()
            return None

    # ── หยุดเกม ───────────────────────────────────────────────────────────────

    def stop_game(self):
        self.is_playing = False
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        self._stop(self.Duringquiz_sound)
        self._stop(self.warning_sound)
        self._stop(self.explosion_sound)
        print("Game stop.")

    # ── สรุปผล ────────────────────────────────────────────────────────────────

    def get_summary(self):
        summary_data = {
            "mode":          self.game_mode,
            "level":         self.level_key,
            "score":         self.score,
            "p1_score":      self.p1_score,
            "p2_score":      self.p2_score,
            "max_combo":     self.max_combo,
            "correct_count": self.correct_count,
            "lives_left":    self.lives,
            "status":        "Finished" if self.lives > 0 else "Game Over",
        }
        print(f"Game Summary: {summary_data}")
        return summary_data

    def use_hint(self):
        if self.hint_used or not self.current_question:
            return "ไม่สามารถใช้ตัวช่วยได้!"
        self.hint_used    = True
        self.score        = max(0, self.score - 1)
        self.hint_message = self.current_question.get('hint', 'ไม่มีคำใบ้สำหรับข้อนี้')
        print(f"Hint Activated: {self.hint_message}")
        return self.hint_message

    # ── รีเซ็ต ────────────────────────────────────────────────────────────────

    def reset_game(self):
        self.stop_game()
        self.score          = 0
        self.p1_score       = 0
        self.p2_score       = 0
        self.current_player = 1
        self.lives          = 3
        self.combo          = 0
        self.max_combo      = 0
        self.correct_count  = 0
        self.all_questions  = []
        self.current_question = None
        self.hint_used      = False
        self.is_playing     = False
        self._reload_sounds()
        print("Game Reset! Ready for new round.")

    # ── ตั้งค่าระดับ ──────────────────────────────────────────────────────────

    def setup_level(self, level_key, mode='single'):
        self.level_key  = level_key
        self.game_mode  = mode
        levels = {
            'easy':   {'time': 15, 'mult': 1.0},
            'medium': {'time': 10, 'mult': 1.5},
            'hard':   {'time': 7,  'mult': 2.5},
            'sudden': {'time': 8,  'mult': 3.0},
            'daily':  {'time': 10, 'mult': 2.0},
        }
        selected              = levels.get(level_key, levels['easy'])
        self.time_left        = selected['time']
        self.score_multiplier = selected['mult']
        print(f"Level Setup: {level_key} mode | Time: {self.time_left}s | Mult: x{self.score_multiplier}")