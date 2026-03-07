from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.app import App
from kivy.animation import Animation

from logic.game_engine import GameEngine
from widgets.game_ui import (
    ClockBombWidget, WireAnswerButton,
    VignetteWidget, ComboDisplay, LivesWidget,
    WIRE_COLORS, WIRE_COLOR_NAMES
)
import random


class GameScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine       = GameEngine()
        self.ui_updater   = None
        self._shuffle_ev  = None
        self.correct_wire = 0
        self.wire_buttons = []
        self.is_waiting   = False
        self.max_time     = 10
        self.q_total      = 5
        self.q_num        = 0

    # ─── เข้าหน้าจอเกม ───────────────────────────────────────────────────────
    def on_enter(self):
        app   = App.get_running_app()
        level = getattr(app, '_level',     'easy')
        mode  = getattr(app, '_game_mode', 'single')
        cat   = getattr(app, '_category',  'general')

        self.engine.reset_game()
        self.engine.setup_level(level, mode)
        self.max_time   = self.engine.time_left
        self.q_num      = 0
        self.is_waiting = False
        self._finishing = False

        if 'timer_bar' in self.ids:
            self.ids.timer_bar.max   = self.max_time
            self.ids.timer_bar.value = self.max_time

        # 2player ใช้ 12 ข้อ (เลขคู่ → แต่ละคนได้ตอบ 6 ข้อ)
        if mode == '2player':
            self.q_total = 12
        else:
            q_counts = {'easy': 5, 'medium': 7, 'hard': 10, 'sudden': 30, 'daily': 5}
            self.q_total = q_counts.get(level, 5)

        try:
            from data.questions import get_questions
            # ── FIX: ส่ง mode ไปด้วยเพื่อให้ get_questions คืน 12 ข้อใน 2player ──
            questions = get_questions(cat, level, mode)
            self.engine.set_questions(questions)
        except Exception as e:
            print(f"[WARN] questions load error: {e}")
            fallback = [
                {
                    "question":     f"คำถามตัวอย่างข้อ {i+1}?",
                    "choices":      ["ตัวเลือก 1", "ตัวเลือก 2", "ตัวเลือก 3", "ตัวเลือก 4"],
                    "answer_index": 0
                }
                for i in range(self.q_total)
            ]
            self.engine.set_questions(fallback)

        self._build_wire_buttons(level)
        self.engine.start_game()

        if self.ui_updater:
            self.ui_updater.cancel()
        self.ui_updater = Clock.schedule_interval(self._tick, 0.1)

        self._load_question()

        if level == 'hard':
            self._shuffle_ev = Clock.schedule_interval(self._shuffle_wires, 2.0)

    def on_leave(self):
        if self.ui_updater:
            self.ui_updater.cancel()
            self.ui_updater = None
        if self._shuffle_ev:
            self._shuffle_ev.cancel()
            self._shuffle_ev = None
        self.wire_buttons = []

    # ─── สร้างปุ่มสายไฟ ──────────────────────────────────────────────────────
    def _build_wire_buttons(self, level):
        wire_count = {'easy': 4, 'medium': 5, 'hard': 6, 'sudden': 5, 'daily': 4}
        n = wire_count.get(level, 4)

        container = self.ids.get('wire_btn_container')
        if not container:
            return
        container.clear_widgets()
        self.wire_buttons = []

        for i in range(n):
            btn = WireAnswerButton()
            btn.wire_index = i
            btn.wire_color = list(WIRE_COLORS[i % len(WIRE_COLORS)])
            btn.text       = ''
            btn.bind(on_release=lambda b, idx=i: self._on_wire_press(idx))
            container.add_widget(btn)
            self.wire_buttons.append(btn)

    # ─── โหลดคำถาม ───────────────────────────────────────────────────────────
    def _load_question(self):
        if 'feedback_label' in self.ids:
            app  = App.get_running_app()
            mode = getattr(app, '_game_mode', 'single')
            e    = self.engine
            if mode == '2player':
                name = app.player_name if e.current_player == 1 else getattr(app, '_p2_name', 'P2')
                self.ids.feedback_label.text = f'ตาของ P{e.current_player}: {name}'
            else:
                self.ids.feedback_label.text = '> แตะปลายสายที่ตรงกับคำตอบ! <'

        q = self.engine.get_next_question()
        if not q:
            self._finish_game()
            return

        self.q_num   += 1
        n             = len(self.wire_buttons)
        choices       = list(q.get('choices', []))
        ans_idx       = q.get('answer_index', 0)
        correct_text  = choices[ans_idx] if ans_idx < len(choices) else choices[0]

        while len(choices) < n:
            choices.append('— ไม่มี —')

        random.shuffle(choices)

        for i, btn in enumerate(self.wire_buttons):
            btn.answered   = False
            btn.is_correct = False
            btn.text = choices[i] if i < len(choices) else ''

        self.correct_wire = 0
        for i, btn in enumerate(self.wire_buttons):
            if btn.text == correct_text:
                self.correct_wire = i
                break

        bomb = self.ids.get('bomb_widget')
        if bomb:
            bomb.reset(self.correct_wire, n)

        self.engine.time_left = self.max_time

        if 'timer_bar' in self.ids:
            self.ids.timer_bar.max   = self.max_time
            self.ids.timer_bar.value = self.max_time

        if 'question_label' in self.ids:
            self.ids.question_label.text = q.get('question', '')

        self._update_hud()

    # ─── กดสายไฟ ─────────────────────────────────────────────────────────────
    def _on_wire_press(self, wire_idx):
        if not self.engine.is_playing or self.is_waiting:
            return

        is_correct = (wire_idx == self.correct_wire)

        if wire_idx < len(self.wire_buttons):
            self.wire_buttons[wire_idx].answered   = True
            self.wire_buttons[wire_idx].is_correct = is_correct

        bomb = self.ids.get('bomb_widget')
        if bomb and wire_idx < len(bomb.wire_states):
            states           = list(bomb.wire_states)
            states[wire_idx] = 0 if is_correct else 1
            bomb.wire_states = states

        if is_correct:
            self._register_correct()
            if bomb:
                bomb.start_defuse()
            combo = self.engine.combo
            if 'feedback_label' in self.ids:
                extra = f'  ** COMBO x{combo}! **' if combo >= 2 else ''
                self.ids.feedback_label.text = f'[ OK ] ถูกต้อง!{extra}'
            if 'combo_display' in self.ids:
                self.ids.combo_display.combo = combo
                self.ids.combo_display.flash()

            if self.engine.game_mode == '2player':
                self._try_switch_player()

            self._update_hud()
            Clock.schedule_once(lambda dt: self._load_question(), 0.7)

        else:
            self._register_wrong()

            if bomb:
                bomb.start_explode()
                self._shake(bomb)
            self.engine.play_explosion()

            if 'vignette' in self.ids:
                self.ids.vignette.pulse_red()

            if self.engine.is_playing:
                self.is_waiting = True
                if self.engine.game_mode == '2player':
                    self._try_switch_player_after_wrong()
                else:
                    if 'feedback_label' in self.ids:
                        self.ids.feedback_label.text = '[ X ] ผิด! หัวใจหายไป 1 ดวง'
                self._update_hud()
                Clock.schedule_once(lambda dt: self._after_wrong(), 1.2)
            else:
                self._update_hud()
                Clock.schedule_once(lambda dt: self._finish_game(), 1.5)

    # ─── สลับผู้เล่นหลังตอบถูก ───────────────────────────────────────────────
    def _try_switch_player(self):
        e    = self.engine
        app  = App.get_running_app()
        next_p     = 2 if e.current_player == 1 else 1
        next_lives = e.p1_lives if next_p == 1 else e.p2_lives

        if next_lives > 0:
            e.current_player = next_p

        name = app.player_name if e.current_player == 1 else getattr(app, '_p2_name', 'P2')
        print(f"[2P] ตาของ P{e.current_player}: {name}")

    # ─── สลับผู้เล่นหลังตอบผิด/หมดเวลา ─────────────────────────────────────
    def _try_switch_player_after_wrong(self):
        e    = self.engine
        app  = App.get_running_app()

        current_lives = e.p1_lives if e.current_player == 1 else e.p2_lives
        next_p        = 2 if e.current_player == 1 else 1
        next_lives    = e.p1_lives if next_p == 1 else e.p2_lives

        if current_lives <= 0:
            if next_lives > 0:
                e.current_player = next_p
                name = app.player_name if e.current_player == 1 else getattr(app, '_p2_name', 'P2')
                if 'feedback_label' in self.ids:
                    self.ids.feedback_label.text = (
                        f'[ X ] P{3 - e.current_player} หมดชีวิตแล้ว!  '
                        f'P{e.current_player}: {name} เล่นต่อ!'
                    )
                print(f"[2P] P{3-e.current_player} หมดชีวิต! -> P{e.current_player} เล่นต่อ")
            else:
                if 'feedback_label' in self.ids:
                    self.ids.feedback_label.text = '[ X ] ทั้งสองทีมหมดชีวิต!'
        else:
            if next_lives > 0:
                e.current_player = next_p
                name = app.player_name if e.current_player == 1 else getattr(app, '_p2_name', 'P2')
                if 'feedback_label' in self.ids:
                    self.ids.feedback_label.text = (
                        f'[ X ] ผิด! หัวใจหายไป 1 ดวง  '
                        f'— ตาของ P{e.current_player}: {name}'
                    )
            else:
                if 'feedback_label' in self.ids:
                    self.ids.feedback_label.text = '[ X ] ผิด! หัวใจหายไป 1 ดวง'

        print(f"[2P] หลังตอบผิด — P1:{e.p1_lives}, P2:{e.p2_lives}, current=P{e.current_player}")

    # ─── คำนวณคะแนน ──────────────────────────────────────────────────────────
    def _register_correct(self):
        e = self.engine
        e.combo         += 1
        e.max_combo      = max(e.max_combo, e.combo)
        e.correct_count += 1
        t_ratio = e.time_left / self.max_time if self.max_time > 0 else 0
        base    = int((t_ratio * 100 + 50) * e.score_multiplier)
        bonus   = max(0, e.combo - 1) * 15
        pts     = base + bonus
        if e.game_mode == '2player':
            if e.current_player == 1:
                e.p1_score += pts
            else:
                e.p2_score += pts
        else:
            e.score += pts
        print(f"Correct! +{pts} pts | Combo x{e.combo}")

    def _register_wrong(self):
        e = self.engine
        e.combo = 0
        e.lose_life()
        if e.both_players_dead() or e.game_mode == 'sudden':
            e.is_playing = False

    # ─── shake animation ─────────────────────────────────────────────────────
    def _shake(self, widget):
        a = (Animation(shake_x=10,  duration=0.06) +
             Animation(shake_x=-10, duration=0.06) +
             Animation(shake_x=7,   duration=0.06) +
             Animation(shake_x=-7,  duration=0.06) +
             Animation(shake_x=0,   duration=0.06))
        a.start(widget)

    def _after_wrong(self):
        self.is_waiting = False
        if self.engine.is_playing:
            self._load_question()
        else:
            self._finish_game()

    def _shuffle_wires(self, dt):
        bomb = self.ids.get('bomb_widget')
        if bomb:
            bomb.shuffle_wires()

    # ─── tick ─────────────────────────────────────────────────────────────────
    def _tick(self, dt):
        if not self.engine.is_playing:
            return

        t     = self.engine.time_left
        ratio = t / self.max_time if self.max_time > 0 else 0

        bomb = self.ids.get('bomb_widget')
        if bomb:
            bomb.time_ratio   = ratio
            bomb.time_display = str(int(t))
            if ratio < 0.25:
                bomb.anim_countdown()

        if 'timer_bar' in self.ids:
            self.ids.timer_bar.value = max(0, min(t, self.max_time))

        if 'vignette' in self.ids:
            if ratio < 0.25:
                self.ids.vignette.pulse_red()
            elif ratio < 0.5:
                self.ids.vignette.show(0.35)
            else:
                self.ids.vignette.hide()

        if 'lbl_timer' in self.ids:
            self.ids.lbl_timer.text = str(int(t))

        if t <= 0 and not self.is_waiting:
            self._on_time_up()

    # ─── หมดเวลา ─────────────────────────────────────────────────────────────
    def _on_time_up(self):
        self.is_waiting = True
        e = self.engine
        e.combo = 0
        e.lose_life()

        if 'vignette' in self.ids:
            self.ids.vignette.pulse_red()
        bomb = self.ids.get('bomb_widget')
        if bomb:
            bomb.start_explode()
            self._shake(bomb)
        self.engine.play_explosion()

        if e.both_players_dead() or e.game_mode == 'sudden':
            e.game_over()
            if 'feedback_label' in self.ids:
                self.ids.feedback_label.text = '[ ! ] หมดเวลา! จบเกม!'
            self._update_hud()
            Clock.schedule_once(lambda dt: self._finish_game(), 1.5)
        else:
            if e.game_mode == '2player':
                self._try_switch_player_after_wrong()
            else:
                if 'feedback_label' in self.ids:
                    self.ids.feedback_label.text = '[ ! ] หมดเวลา! หัวใจหายไป 1 ดวง'
            self._update_hud()
            Clock.schedule_once(lambda dt: self._after_wrong(), 1.5)

    # ─── HUD ─────────────────────────────────────────────────────────────────
    def _update_hud(self):
        app  = App.get_running_app()
        mode = getattr(app, '_game_mode', 'single')
        lvl  = getattr(app, '_level', 'easy')
        e    = self.engine

        if 'lbl_player' in self.ids:
            if mode == '2player':
                p    = 'P1' if e.current_player == 1 else 'P2'
                name = app.player_name if e.current_player == 1 else getattr(app, '_p2_name', 'P2')
                self.ids.lbl_player.text = f'{p}: {name}'
            else:
                self.ids.lbl_player.text = f'{app.player_name}'

        if 'lbl_score' in self.ids:
            if mode == '2player':
                score = e.p1_score if e.current_player == 1 else e.p2_score
            else:
                score = e.score
            self.ids.lbl_score.text = f'{score} pts'

        if 'lbl_lives' in self.ids:
            if lvl == 'sudden':
                self.ids.lbl_lives.lives     = 0
                self.ids.lbl_lives.max_lives = 0
                self.ids.lbl_lives.is_sudden = True
            elif mode == '2player':
                current_lives = e.p1_lives if e.current_player == 1 else e.p2_lives
                self.ids.lbl_lives.lives     = max(0, current_lives)
                self.ids.lbl_lives.max_lives = 3
                self.ids.lbl_lives.is_sudden = False
            else:
                self.ids.lbl_lives.lives     = max(0, e.lives)
                self.ids.lbl_lives.max_lives = 3
                self.ids.lbl_lives.is_sudden = False

        if 'lbl_timer' in self.ids:
            self.ids.lbl_timer.text = str(int(e.time_left))

        if 'lbl_qnum' in self.ids:
            total = 'inf' if lvl == 'sudden' else str(self.q_total)
            self.ids.lbl_qnum.text = f'{self.q_num}/{total}'

    # ─── จบเกม ────────────────────────────────────────────────────────────────
    def _finish_game(self):
        if getattr(self, '_finishing', False):
            return
        self._finishing = True

        if self.ui_updater:
            self.ui_updater.cancel()
            self.ui_updater = None
        if self._shuffle_ev:
            self._shuffle_ev.cancel()
            self._shuffle_ev = None

        if self.engine.is_playing:
            self.engine.game_over()
        else:
            if self.engine.timer_event:
                self.engine.timer_event.cancel()
                self.engine.timer_event = None
            if getattr(self.engine, 'Duringquiz_sound', None):
                self.engine.Duringquiz_sound.stop()
            if getattr(self.engine, 'warning_sound', None):
                self.engine.warning_sound.stop()

        summary = self.engine.get_summary()
        app     = App.get_running_app()

        try:
            from data.leaderboard_mgr import save_score
            cat   = getattr(app, '_category', 'general')
            level = getattr(app, '_level',    'easy')
            mode  = summary.get('mode', 'single')
            if mode == '2player':
                save_score(app.player_name,
                           summary.get('p1_score', 0), cat, level)
                save_score(getattr(app, '_p2_name', 'Player 2'),
                           summary.get('p2_score', 0), cat, level)
            else:
                save_score(app.player_name, summary.get('score', 0), cat, level)
        except Exception as ex:
            print(f"[WARN] leaderboard save: {ex}")

        new_ach = []
        try:
            from data.leaderboard_mgr import check_and_unlock
            new_ach = check_and_unlock(summary)
        except Exception as ex:
            print(f"[WARN] achievement check: {ex}")

        try:
            result = self.manager.get_screen('result')
            self._fill_result(result, summary, new_ach)
        except Exception as ex:
            print(f"[WARN] result screen: {ex}")

        if self.manager:
            self.manager.current = 'result'

    def _fill_result(self, result, summary, new_ach=None):
        app  = App.get_running_app()
        mode = summary.get('mode', 'single')
        lvl  = getattr(app, '_level', 'easy')

        if mode == '2player':
            p1s           = summary.get('p1_score', 0)
            p2s           = summary.get('p2_score', 0)
            p1_lives_left = max(0, summary.get('p1_lives', 0))
            p2_lives_left = max(0, summary.get('p2_lives', 0))
            p2n           = getattr(app, '_p2_name', 'Player 2')
            winner        = app.player_name if p1s >= p2s else p2n

            result.ids.lbl_result_title.text = 'จบการแข่งขัน!'
            result.ids.lbl_result_agent.text = f'{winner} ชนะ!'
            result.ids.lbl_result_score.text = f'P1: {p1s} pts  vs  P2: {p2s} pts'
            result.ids.lbl_result_stats.text = (
                f'P1 ชีวิต: {p1_lives_left}/3'
                f'  |  P2 ชีวิต: {p2_lives_left}/3'
                f'  |  Max Combo x{summary.get("max_combo", 0)}'
            )
            result.ids.lbl_result_msg.text = ''
        else:
            score = summary.get('score', 0)
            cc    = summary.get('correct_count', 0)
            mc    = summary.get('max_combo', 0)

            if lvl == 'sudden':
                result.ids.lbl_result_title.text = 'เกมโอเวอร์!'
                result.ids.lbl_result_stats.text = f'รอด {cc} ข้อ  |  Max Combo x{mc}'
            else:
                result.ids.lbl_result_title.text = 'ภารกิจสำเร็จ!'
                result.ids.lbl_result_stats.text = f'ถูก {cc} ข้อ  |  Max Combo x{mc}'

            result.ids.lbl_result_agent.text = f'AGENT: {app.player_name}'
            result.ids.lbl_result_score.text = f'{score} pts'

            msgs = {
                'easy':   'ระเบิดถูกปลดชนวนแล้ว!',
                'medium': 'ยอดเยี่ยม! คุณผ่านมาได้!',
                'hard':   'เก่งมาก! โหมดยากไม่ยากเลย!',
                'sudden': f'อยู่รอดได้ {cc} ข้อ!',
                'daily':  'เสร็จสิ้นภารกิจประจำวัน!',
            }
            result.ids.lbl_result_msg.text = msgs.get(lvl, 'ดีมาก!')

        try:
            from data.leaderboard_mgr import get_rank
            rank = get_rank(summary.get('score', 0))
            result.ids.lbl_rank.text = f'#{rank} อันดับที่ {rank}!'
        except Exception:
            result.ids.lbl_rank.text = ''

        if new_ach:
            ach_text = '  '.join([a["name"] for a in new_ach])
            result.ids.lbl_new_ach.text = f'ปลดล็อก: {ach_text}'
        else:
            result.ids.lbl_new_ach.text = ''