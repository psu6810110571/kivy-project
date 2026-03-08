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

        self.lives         = 3   # ใช้สำหรับ single / daily
        self.p1_lives      = 3   # sync กับ lives ใน single/daily, ชีวิต P1 ใน 2player
        self.p2_lives      = 3   # ชีวิต P2 สำหรับ 2player
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

        # FIX: flag ว่าเกมจบจาก sudden death หรือเปล่า
        self._sudden_dead = False
        
        # [เพิ่มใหม่] ตัวแปรเก็บแต้มโบนัส Perfect Clear
        self.perfect_bonus = 0

        self._reload_sounds()

    # ── เสียง ─────────────────────────────────────────────────────────────────

    def _reload_sounds(self):
        self.Duringquiz_sound = _load_sound('assets/sounds/Duringquiz.wav')
        self.warning_sound    = _load_sound('assets/sounds/warning.wav')
        self.explosion_sound  = _load_sound('assets/sounds/explosion.wav')
        self.correct_sound    = _load_sound('assets/sounds/correct.mp3')

        if self.Duringquiz_sound:
            self.Duringquiz_sound.loop   = True
            self.Duringquiz_sound.volume = 1.0
        if self.warning_sound:
            self.warning_sound.volume = 1.0
        if self.explosion_sound:
            self.explosion_sound.volume = 1.0
        if self.correct_sound:
            self.correct_sound.volume = 1.0

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
        self._stop(self.Duringquiz_sound)
        self._stop(self.warning_sound)
        self._play(self.explosion_sound)

    def play_correct(self):
        self._play(self.correct_sound)

    def restart_bgm(self):
        """เปิด BGM กลับหลังโหลดข้อใหม่ — หยุด warning ก่อนแล้วเล่น BGM"""
        self._stop(self.warning_sound)
        self._stop(self.explosion_sound)
        if self.Duringquiz_sound and self.is_playing:
            self.Duringquiz_sound.volume = 1.0
            self.Duringquiz_sound.play()

    # ── ชีวิตของผู้เล่นปัจจุบัน ──────────────────────────────────────────────

    def get_current_lives(self):
        if self.game_mode == '2player':
            return self.p1_lives if self.current_player == 1 else self.p2_lives
        return self.lives

    def lose_life(self):
        """
        หักชีวิตผู้เล่นปัจจุบัน
        - 2player      : หักเฉพาะ p1_lives หรือ p2_lives
        - single/daily : หัก lives และ sync p1_lives
        - sudden       : ไม่มีระบบชีวิต — set flag _sudden_dead แทน
        """
        if self.game_mode == '2player':
            if self.current_player == 1:
                self.p1_lives = max(0, self.p1_lives - 1)
                remaining = self.p1_lives
            else:
                self.p2_lives = max(0, self.p2_lives - 1)
                remaining = self.p2_lives
        elif self.game_mode == 'sudden':
            # sudden death — ไม่มีชีวิต แค่ mark ว่าตายแล้ว
            self._sudden_dead = True
            remaining = 0
        else:
            # single / daily
            self.lives    = max(0, self.lives - 1)
            self.p1_lives = self.lives
            remaining = self.lives

        print(f"[LIFE] P{self.current_player} lives: {remaining}")
        return remaining

    def both_players_dead(self):
        """คืน True ถ้าเกมควรจบแล้ว"""
        if self.game_mode == 'sudden':
            return self._sudden_dead   # FIX: sudden ใช้ flag แทน lives
        if self.game_mode == '2player':
            return self.p1_lives <= 0 and self.p2_lives <= 0
        return self.lives <= 0

    def current_player_dead(self):
        return self.get_current_lives() <= 0

    # ── เริ่มเกม ──────────────────────────────────────────────────────────────

    def start_game(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

        # ── 🕵️‍♂️ ระบบ Easter Egg (Cheat Code) ─────────────────────────
        try:
            from kivy.app import App
            app = App.get_running_app()
            # ดึงชื่อผู้เล่นมาแปลงเป็นตัวพิมพ์เล็กทั้งหมดเพื่อเช็กง่ายๆ
            p_name = getattr(app, 'player_name', '').strip().lower()
            
            # ถ้ารหัสลับตรงกับที่ตั้งไว้ ให้บัฟพลังทันที!
            if p_name in ['chin', 'max', 'gus']:
                print(f"[SECRET] Cheat Activated by '{p_name}'! 99 Lives & x2 Score!")
                self.lives = 99
                self.p1_lives = 99
                self.p2_lives = 99
                self.score_multiplier *= 2
        except Exception as e:
            print(f"[SECRET] Error checking cheat code: {e}")
        # ──────────────────────────────────────────────────────────────

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

    # ── ตรวจคำตอบ (เพิ่มสูตรโบนัสความไว) ────────────────────────────────────

    def check_answer(self, user_answer_index, correct_answer_index):
        if not self.current_question:
            return False
        correct_answer_index = self.current_question.get('answer_index', 0)
        if user_answer_index == correct_answer_index:
            self.combo         += 1
            self.max_combo      = max(self.max_combo, self.combo)
            self.correct_count += 1
            
            # 1. คะแนนพื้นฐาน
            base_points  = 100
            
            # 2. โบนัสความไว (Speed Bonus) คิดจากเปอร์เซ็นต์เวลาที่เหลือ
            level_times = {'easy': 15, 'medium': 10, 'hard': 7, 'sudden': 8, 'daily': 10}
            max_t = level_times.get(self.level_key, 10)
            t_ratio = self.time_left / max_t if max_t > 0 else 0
            speed_bonus = int(t_ratio * 150) # ตอบเร็วยิ่งได้โบนัสเยอะ สูงสุด 150 แต้ม
            
            # 3. โบนัสคอมโบ
            combo_bonus  = max(0, self.combo - 1) * 15
            
            # รวมคะแนนแล้วคูณ
            total_points = int((base_points + speed_bonus + combo_bonus) * self.score_multiplier)
            
            if self.game_mode == '2player':
                if self.current_player == 1:
                    self.p1_score += total_points
                else:
                    self.p2_score += total_points
            else:
                self.score    += total_points
                self.p1_score  = self.score
                
            print(f"Correct! +{total_points} pts | Speed Bonus: {speed_bonus} | Combo: x{self.combo}")
            return True
        else:
            self.combo = 0
            self.lose_life()
            if self.both_players_dead() or self.game_mode == 'sudden':
                self.game_over()
            return False

    def time_up(self):
        if not self.is_playing:
            return
        self.combo = 0
        self.lose_life()
        if self.both_players_dead() or self.game_mode == 'sudden':
            self.game_over()

    # ── [เพิ่มใหม่] โบนัส Perfect Clear ─────────────────────────────────────────
    def _apply_perfect_clear_bonus(self):
        bonus_points = 1000
        # ถ้าเป็นโหมด 2player ใครหัวใจไม่ลดเลย เอาโบนัสไปเลย!
        if self.game_mode == '2player':
            if self.p1_lives in [3, 99]:
                self.p1_score += bonus_points
                self.perfect_bonus = bonus_points
            if self.p2_lives in [3, 99]:
                self.p2_score += bonus_points
                self.perfect_bonus = bonus_points
        # โหมดทั่วไป (ยกเว้น Sudden Death ที่ไม่มีวันจบ)
        elif self.game_mode != 'sudden':
            if self.lives in [3, 99]:
                self.score += bonus_points
                self.p1_score = self.score
                self.perfect_bonus = bonus_points

    # ── จบเกม ─────────────────────────────────────────────────────────────────

    def game_over(self):
        self.is_playing = False
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        self._stop(self.Duringquiz_sound)
        self._stop(self.warning_sound)
        print(f"BOOM! Game Over! Final Score: {self.score}")

    # ── คำถาม ─────────────────────────────────────────────────────────────────

    def set_questions(self, question_list):
        self.all_questions = question_list.copy()
        random.shuffle(self.all_questions)
        print(f"Loaded {len(self.all_questions)} questions and shuffled!")

    def get_next_question(self):
        if len(self.all_questions) > 0:
            self.current_question = self.all_questions.pop(0)
            self.hint_used = False  # รีเซ็ตคำใบ้เมื่อเปลี่ยนข้อ

            # --- 🎲 ระบบสุ่มตัวเลือก (Shuffle Choices) ---
            original_answer_idx = self.current_question.get('answer_index', 0)
            original_choices = self.current_question.get('choices', [])
            
            if original_choices:
                # 1. จำข้อความที่เป็นคำตอบที่ถูกต้องเอาไว้ก่อน
                correct_text = original_choices[original_answer_idx]
                
                # 2. ทำสำเนาตัวเลือก แล้วสับเปลี่ยนตำแหน่ง
                shuffled_choices = original_choices.copy()
                random.shuffle(shuffled_choices)
                
                # 3. หาว่าคำตอบที่ถูก ย้ายไปอยู่ Index ใหม่ที่เท่าไหร่
                new_answer_idx = shuffled_choices.index(correct_text)
                
                # 4. อัปเดตกลับเข้าไปใน current_question
                self.current_question['choices'] = shuffled_choices
                self.current_question['answer_index'] = new_answer_idx
            # -----------------------------------------------

            return self.current_question
        else:
            print("No more questions!")
            # [เพิ่มใหม่] แจกโบนัสก่อนจบเกมถ้าตอบครบแล้วไม่ตายเลย
            self._apply_perfect_clear_bonus()
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
        if self.game_mode != '2player':
            self.p1_score = self.score

        # FIX: ดึงค่า lives_left ให้ตรงกับโหมดที่เล่นจริงๆ
        if self.game_mode == 'sudden':
            actual_lives = 0 if self._sudden_dead else 1
        elif self.game_mode == '2player':
            actual_lives = max(self.p1_lives, self.p2_lives)
        else:
            actual_lives = self.lives

        summary_data = {
            "mode":          self.game_mode,
            "level":         self.level_key,
            "score":         self.score,
            "p1_score":      self.p1_score,
            "p2_score":      self.p2_score,
            "p1_lives":      self.p1_lives,
            "p2_lives":      self.p2_lives,
            "max_combo":     self.max_combo,
            "correct_count": self.correct_count,
            "lives_left":    actual_lives,
            "status":        "Game Over" if self.both_players_dead() else "Finished",
            "perfect_bonus": self.perfect_bonus # [เพิ่มใหม่] ส่งค่าโบนัสให้หน้าจอ
        }
        print(f"Game Summary: {summary_data}")
        return summary_data

    # ── ระบบคำใบ้ (อัปเดตหักคะแนน 20%) ──────────────────────────────────────────
    
    def use_hint(self):
        if self.hint_used or not self.current_question:
            return ("ใช้คำใบ้ไปแล้วในข้อนี้!", 0)
        self.hint_used    = True
        
        penalty = 0
        if self.game_mode == '2player':
            if self.current_player == 1:
                penalty = int(self.p1_score * 0.20)
                self.p1_score = max(0, self.p1_score - penalty)
            else:
                penalty = int(self.p2_score * 0.20)
                self.p2_score = max(0, self.p2_score - penalty)
        else:
            penalty = int(self.score * 0.20)
            self.score = max(0, self.score - penalty)
            
        self.hint_message = self.current_question.get('hint', 'ไม่มีคำใบ้สำหรับข้อนี้')
        print(f"Hint Activated: {self.hint_message} (-{penalty} pts)")
        return (self.hint_message, penalty)

    # ── รีเซ็ต ────────────────────────────────────────────────────────────────

    def reset_game(self):
        self.stop_game()
        self.score          = 0
        self.p1_score       = 0
        self.p2_score       = 0
        self.current_player = 1
        self.lives          = 3
        self.p1_lives       = 3
        self.p2_lives       = 3
        self.combo          = 0
        self.max_combo      = 0
        self.correct_count  = 0
        self.all_questions  = []
        self.current_question = None
        self.hint_used      = False
        self.is_playing     = False
        self._sudden_dead   = False   # FIX: reset flag ด้วย
        self.perfect_bonus  = 0       # [เพิ่มใหม่] รีเซ็ตโบนัส
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