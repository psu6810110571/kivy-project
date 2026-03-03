import os

# Fix Thai text/diacritic overlap on some Windows setups by using PIL text provider.
# Must be set before importing Kivy.
os.environ.setdefault('KIVY_TEXT', 'pil')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.animation import Animation
from kivy.clock import Clock
import random # <--- นำเข้า random สำหรับสุ่มคำถาม

# ── 1. โหลด Font จากโฟลเดอร์ assets ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LabelBase.register(
    name='Sarabun',
    fn_regular=os.path.join(BASE_DIR, 'assets', 'Sarabun-Regular.ttf'),
    fn_bold   =os.path.join(BASE_DIR, 'assets', 'Sarabun-Bold.ttf'),
)

# ── 2. ดึงวิดเจ็ตและข้อมูลคำถาม ───────────────────────────────────────────────────
from widgets.bomb import BombWidget
from widgets.game_ui import VignetteWidget, ComboDisplay

from logic.game_engine import GameEngine

# <--- [เชื่อมต่อไฟล์คำถาม] --->
from data.questions import QUESTIONS, DAILY_QUESTIONS
# <------------------------>

# ── 3. หน้าจอต่างๆ ─────────────────────────────────────────────────────────────
class MenuScreen(Screen):
    def on_enter(self):
        title = self.ids.get('title_label')
        if title:
            title.opacity = 0
            Animation(opacity=1, duration=1.0, t='in_cubic').start(title)

class BriefingScreen(Screen):    
    pass                         

class CategoryScreen(Screen):
    pass

class ModeScreen(Screen):
    pass

class LevelScreen(Screen):
    pass

class Player2SetupScreen(Screen):
    pass

class GameScreen(Screen):
    pass

class ResultScreen(Screen):
    pass

class LeaderboardScreen(Screen):
    pass

class AchievementScreen(Screen):
    pass

# ── 4. ตัวควบคุมแอปหลัก ─────────────────────────────────────────────────────────────
class QuizApp(App):
    player_name = StringProperty('Unknown Agent')
    
    # <--- [เพิ่มตัวแปร LEVELS ตามกติกาของเพื่อนคุณ] --->
    LEVELS = {
        'easy':   {'label': '🟢 ง่าย',   'time': 15, 'wires': 4, 'q_count': 5,  'mult': 1.0},
        'medium': {'label': '🟡 กลาง',   'time': 10, 'wires': 5, 'q_count': 7,  'mult': 1.5},
        'hard':   {'label': '🔴 ยาก',    'time':  7, 'wires': 6, 'q_count': 10, 'mult': 2.5},
        'sudden': {'label': '💀 Sudden', 'time':  8, 'wires': 5, 'q_count': 99, 'mult': 3.0},
        'daily':  {'label': '📅 Daily',  'time': 10, 'wires': 4, 'q_count': 5,  'mult': 2.0},
    }
    # <------------------------------------------------>

    def fade_transition(self):
        return FadeTransition(duration=0.3)

    def build(self):
        root = Builder.load_file('quiz.kv')
        self.engine = GameEngine()
        self._engine_watcher = None
        self._current_level = self.LEVELS['easy']
        self._q_number = 0
        return root

    def btn_press_anim(self, btn):
        a = (Animation(opacity=0.7, duration=0.08) +
             Animation(opacity=1.0, duration=0.08))
        a.start(btn)

    def go_to_category(self, name):
        self.player_name = name.strip() or 'Unknown Agent'
        print(f"Agent '{self.player_name}' is ready!")
        self.root.current = 'category'

    def select_category(self, category):
        print(f"หมวดหมู่ที่เลือก: {category}")
        self._category = category
        self.root.current = 'mode'
    
    def set_mode(self, mode):
        print(f"โหมดที่เลือก: {mode}")
        self._game_mode = mode
        if mode == 'single':
            self.root.current = 'level'
        elif mode == '2player':
            self.root.current = 'p2setup'
        else:
            print(f"กำลังเริ่มเกมโหมดพิเศษ: {mode}")
            # โหมดพิเศษไม่ต้องเลือกระดับ แต่อาศัยกติกาที่กำหนดไว้ใน LEVELS
            if mode == 'sudden':
                self.start_game('sudden')
            elif mode == 'daily':
                self.start_game('daily')

    def start_2player(self, p2name):
        self._p2_name = p2name.strip() or 'Player 2'
        print(f"ตั้งชื่อผู้เล่น 2 สำเร็จ: {self._p2_name}")
        self.start_game('medium')

    # <--- [อัปเดตฟังก์ชันเริ่มเกมให้รองรับความยาก] --->
    def start_game(self, level_key):
        print(f"กำลังเริ่มเกมระดับ: {level_key}...")

        # ดึงกติกาของระดับ/โหมด
        self._current_level = self.LEVELS.get(level_key, self.LEVELS['easy'])
        game_mode = getattr(self, '_game_mode', 'single')

        # เตรียมคำถามตามโหมด
        category = getattr(self, '_category', 'general')
        if level_key == 'daily' or game_mode == 'daily':
            q_list = DAILY_QUESTIONS[:]
        else:
            q_list = QUESTIONS.get(category, QUESTIONS['general'])[:]
        random.shuffle(q_list)

        # กำหนดจำนวนข้อตามกติกา
        num_questions = self._current_level.get('q_count', len(q_list))
        selected_questions = q_list[:num_questions]

        # รีเซ็ตและตั้งค่า engine ให้เป็นตัวคุมเกมหลัก
        if getattr(self, 'engine', None) is None:
            self.engine = GameEngine()
        self.engine.reset_game()
        self.engine.setup_level(level_key, mode=game_mode)
        self.engine.set_questions(selected_questions)
        self.engine.start_game()

        # watcher คอยเช็คว่า engine จบเกมจากเวลาหมด/หัวใจหมดหรือยัง
        if self._engine_watcher:
            self._engine_watcher.cancel()
        self._engine_watcher = Clock.schedule_interval(self._watch_engine_state, 0.2)

        self._q_number = 0
        print(f"✅ โหลดคำถามสำเร็จ! จำนวน {len(selected_questions)} ข้อ | โหมด {game_mode} | หมวด {category}")

        self.root.current = 'game'
        self.load_question()
    # <----------------------------------------->

    # <--- [อัปเดตระบบดึงคำถามและตัวเลือกตามความยาก] --->
    def load_question(self):
        # ดึงคำถามจาก engine
        if not getattr(self, 'engine', None):
            print("⚠️ engine ยังไม่พร้อม")
            return

        raw_q = self.engine.get_next_question()
        if not raw_q:
            self.show_result()
            return

        self._q_number += 1
        game_screen = self.root.get_screen('game')

        # แปลงคำถามจาก data/questions.py ให้เป็นรูปแบบที่ engine ตรวจคำตอบได้ตรงกับปุ่มที่แสดง
        display_q = self._build_display_question(raw_q)
        self.engine.current_question = display_q

        if 'lbl_question' in game_screen.ids:
            game_screen.ids.lbl_question.text = f"ข้อที่ {self._q_number}: {display_q['question']}"

        if 'answer_grid' in game_screen.ids:
            ans_grid = game_screen.ids.answer_grid
            ans_grid.clear_widgets()

            num_choices = len(display_q['choices'])
            ans_grid.cols = 2 if num_choices <= 4 else 3

            for idx, ans in enumerate(display_q['choices']):
                btn = Button(text=ans, font_name='Sarabun', font_size=sp(16))
                btn.answer_index = idx
                btn.bind(on_release=self.check_answer)
                ans_grid.add_widget(btn)

    def check_answer(self, instance):
        print(f"ผู้เล่นกดเลือกตอบ: {instance.text}")

        if not getattr(self, 'engine', None) or not self.engine.is_playing:
            return

        selected_idx = getattr(instance, 'answer_index', None)
        if selected_idx is None:
            return

        is_correct = self.engine.check_answer(selected_idx, None)
        if not is_correct:
            # กรณีผิด/หัวใจหมด: engine จะจัดการเอง
            pass

        if not self.engine.is_playing:
            self.show_result()
            return

        self.load_question()
    # <------------------------------------------------------------------------>

    def play_again(self):
        print("เริ่มเล่นใหม่อีกครั้ง!")
        if getattr(self, 'engine', None):
            self.engine.reset_game()
        self.root.current = 'category'

    def go_home(self):
        if getattr(self, 'engine', None):
            self.engine.stop_game()
        self.root.current = 'menu'

    def _watch_engine_state(self, dt):
        if not getattr(self, 'engine', None):
            return
        if not self.engine.is_playing:
            if self._engine_watcher:
                self._engine_watcher.cancel()
                self._engine_watcher = None
            # ถ้าเกมจบในขณะที่ยังอยู่หน้าเกม ให้ไปสรุปผล
            if self.root and self.root.current == 'game':
                self.show_result()

    def show_result(self):
        if self._engine_watcher:
            self._engine_watcher.cancel()
            self._engine_watcher = None

        if not getattr(self, 'engine', None):
            self.root.current = 'result'
            return

        summary = self.engine.get_summary()
        try:
            result_screen = self.root.get_screen('result')
            if 'lbl_result_agent' in result_screen.ids:
                result_screen.ids.lbl_result_agent.text = f"AGENT: {self.player_name}"
            if 'lbl_result_score' in result_screen.ids:
                # โหมด 2 ผู้เล่น ถ้ามีคะแนนจะโชว์รวมแบบง่าย
                if summary.get('mode') == '2player':
                    total = int(summary.get('p1_score', 0)) + int(summary.get('p2_score', 0))
                    result_screen.ids.lbl_result_score.text = f"{total} pts"
                else:
                    result_screen.ids.lbl_result_score.text = f"{int(summary.get('score', 0))} pts"
            if 'lbl_result_stats' in result_screen.ids:
                stats = f"Combo สูงสุด: {summary.get('max_combo', 0)} | ตอบถูก: {summary.get('correct_count', 0)}"
                result_screen.ids.lbl_result_stats.text = stats
        except Exception as e:
            print(f"ไม่สามารถอัปเดตหน้าผลลัพธ์ได้: {e}")

        self.root.current = 'result'

    def _build_display_question(self, raw_q):
        """สร้างคำถามสำหรับแสดงบน UI ให้สอดคล้องกับจำนวนตัวเลือกตามระดับ และให้ engine ตรวจคำตอบได้"""
        q_text = raw_q.get('q') or raw_q.get('question') or ''
        all_answers = raw_q.get('a') or raw_q.get('choices') or []
        correct_index = raw_q.get('correct', raw_q.get('answer_index', 0))

        try:
            correct_text = all_answers[int(correct_index)]
        except Exception:
            correct_text = all_answers[0] if all_answers else ''

        wrong_answers = [ans for i, ans in enumerate(all_answers) if ans != correct_text]
        random.shuffle(wrong_answers)

        num_wires = int(self._current_level.get('wires', min(4, max(2, len(all_answers) or 4))))
        # ถ้าตัวเลือกน้อยกว่า wires ก็ใช้เท่าที่มี
        desired_wrong = max(0, min(len(wrong_answers), num_wires - 1))
        chosen_answers = wrong_answers[:desired_wrong]
        if correct_text:
            chosen_answers.append(correct_text)
        random.shuffle(chosen_answers)

        # หา index ของคำตอบถูกในชุดที่แสดง
        answer_index = chosen_answers.index(correct_text) if correct_text in chosen_answers else 0
        return {
            'question': q_text,
            'choices': chosen_answers,
            'answer_index': answer_index,
            'hint': raw_q.get('hint', '')
        }

    def show_leaderboard(self):
        self._lb_prev = self.root.current 
        self.root.current = 'leaderboard'

    def go_back_from_lb(self):
        self.root.current = getattr(self, '_lb_prev', 'menu')

    def show_achievements(self):
        self.root.current = 'achievements'

if __name__ == '__main__':
    QuizApp().run()