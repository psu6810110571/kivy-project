import json
import os

# ══════════════════════════════════════════════════════════════════════════════
#  leaderboard_mgr.py  —  จัดการ Leaderboard และ Achievements
# ══════════════════════════════════════════════════════════════════════════════

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
LB_FILE     = os.path.join(BASE_DIR, '..', 'leaderboard.json')
ACH_FILE    = os.path.join(BASE_DIR, '..', 'achievements.json')
MAX_ENTRIES = 20

# ─── นิยาม Achievements (ไม่ใช้ emoji — ใช้ตัวอักษรแทน) ──────────────────────
ACHIEVEMENTS = [
    {"id": "first_blood",  "icon": "[FB]",  "name": "First Blood",  "desc": "เล่นครั้งแรก"},
    {"id": "on_fire",      "icon": "[HOT]", "name": "On Fire",      "desc": "Combo x5 ขึ้นไป"},
    {"id": "perfect",      "icon": "[*]",   "name": "Perfect",      "desc": "ตอบถูกทุกข้อใน 1 เกม"},
    {"id": "speedster",    "icon": "[>>]",  "name": "Speedster",    "desc": "ตอบถูกภายใน 2 วินาที"},
    {"id": "survivor",     "icon": "[SK]",  "name": "Survivor",     "desc": "เล่น Sudden Death ผ่าน 5 ข้อ"},
    {"id": "daily_agent",  "icon": "[D]",   "name": "Daily Agent",  "desc": "ทำ Daily Challenge สำเร็จ"},
    {"id": "hard_cleared", "icon": "[H]",   "name": "Hard Cleared", "desc": "ผ่าน Hard โดยไม่เสียชีวิต"},
    {"id": "boss_slayer",  "icon": "[BS]",  "name": "Boss Slayer",  "desc": "ผ่าน Boss Round สำเร็จ"},
    {"id": "tag_team",     "icon": "[2P]",  "name": "Tag Team",     "desc": "ชนะโหมด 2 ผู้เล่น"},
]


# ══════════════════════════════════════════════════════════════════════════════
#  Leaderboard
# ══════════════════════════════════════════════════════════════════════════════

def _load_lb() -> list:
    try:
        if os.path.exists(LB_FILE):
            with open(LB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"[LB] load error: {e}")
    return []


def _save_lb(data: list):
    try:
        with open(LB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[LB] save error: {e}")


def save_score(name: str, score: int, category: str = 'general', level: str = 'easy'):
    """บันทึกคะแนนลง leaderboard.json"""
    if score <= 0:
        return
    data = _load_lb()
    entry = {
        "name":     name,
        "score":    score,
        "category": category,
        "level":    level,
    }
    data.append(entry)
    data.sort(key=lambda x: x['score'], reverse=True)
    data = data[:MAX_ENTRIES]
    _save_lb(data)
    print(f"[LB] saved: {name} -> {score} pts ({category}/{level})")


def load_scores() -> list:
    """โหลดคะแนนทั้งหมด เรียงจากมากไปน้อย"""
    return _load_lb()


def get_rank(score: int) -> int:
    """คืนอันดับของคะแนนนี้ใน leaderboard (1 = สูงสุด)"""
    data = _load_lb()
    for i, entry in enumerate(data):
        if score >= entry['score']:
            return i + 1
    return len(data) + 1


def populate_leaderboard(grid_widget):
    """เติมข้อมูลลงใน GridLayout ของ LeaderboardScreen"""
    from kivy.uix.label import Label
    from kivy.uix.boxlayout import BoxLayout
    from kivy.graphics import Color, RoundedRectangle
    from kivy.metrics import dp, sp

    grid_widget.clear_widgets()
    data = _load_lb()

    if not data:
        lbl = Label(
            text='ยังไม่มีคะแนน\nเล่นเกมก่อนแล้วกลับมาดู!',
            font_name='Sarabun', font_size=sp(16),
            color=(0.6, 0.6, 0.8, 1), halign='center',
            size_hint_y=None, height=dp(80)
        )
        grid_widget.add_widget(lbl)
        return

    # ใช้ตัวอักษรแทน emoji เหรียญ
    medals = {1: '#1', 2: '#2', 3: '#3'}

    for i, entry in enumerate(data[:20], start=1):
        rank_text  = medals.get(i, str(i) + '.')
        name_text  = entry.get('name', '???')
        score_text = str(entry.get('score', 0)) + ' pts'
        mode_text  = f"{entry.get('category','?')}/{entry.get('level','?')}"

        row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None, height=dp(48),
            padding=dp(10), spacing=dp(6)
        )

        if i == 1:
            bg_color = (0.35, 0.27, 0.02, 0.85)
        elif i == 2:
            bg_color = (0.20, 0.20, 0.22, 0.80)
        elif i == 3:
            bg_color = (0.25, 0.12, 0.04, 0.80)
        else:
            bg_color = (0.08, 0.08, 0.18, 0.70)

        with row.canvas.before:
            Color(*bg_color)
            row._bg = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(10)])
        row.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                 size=lambda w, v: setattr(w._bg, 'size', v))

        def _lbl(text, fs=14, color=(1, 1, 1, 1), sh=0.15, bold=False):
            l = Label(text=text, font_name='Sarabun', font_size=sp(fs),
                      color=color, halign='center', bold=bold,
                      size_hint_x=sh)
            return l

        row.add_widget(_lbl(rank_text,  14, (1, 0.85, 0.1, 1),     0.12, bold=(i <= 3)))
        row.add_widget(_lbl(name_text,  15, (1, 1, 1, 1),           0.40, bold=True))
        row.add_widget(_lbl(score_text, 16, (1, 0.75, 0.1, 1),      0.28, bold=True))
        row.add_widget(_lbl(mode_text,  11, (0.55, 0.55, 0.75, 1),  0.20))

        grid_widget.add_widget(row)


# ══════════════════════════════════════════════════════════════════════════════
#  Achievements
# ══════════════════════════════════════════════════════════════════════════════

def _load_ach() -> set:
    try:
        if os.path.exists(ACH_FILE):
            with open(ACH_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
    except Exception as e:
        print(f"[ACH] load error: {e}")
    return set()


def _save_ach(unlocked: set):
    try:
        with open(ACH_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(unlocked), f, ensure_ascii=False)
    except Exception as e:
        print(f"[ACH] save error: {e}")


def unlock_achievement(ach_id: str) -> bool:
    """ปลดล็อก achievement คืนค่า True ถ้าปลดล็อกใหม่"""
    unlocked = _load_ach()
    if ach_id not in unlocked:
        unlocked.add(ach_id)
        _save_ach(unlocked)
        print(f"[ACH] unlocked: {ach_id}")
        return True
    return False


def check_and_unlock(summary: dict) -> list:
    """ตรวจสอบเงื่อนไข achievement จาก summary หลังจบเกม"""
    newly = []

    def try_unlock(aid):
        if unlock_achievement(aid):
            ach = next((a for a in ACHIEVEMENTS if a['id'] == aid), None)
            if ach:
                newly.append(ach)

    try_unlock('first_blood')

    if summary.get('max_combo', 0) >= 5:
        try_unlock('on_fire')

    if summary.get('lives_left', 0) >= 3 and summary.get('correct_count', 0) > 0:
        try_unlock('perfect')

    if summary.get('mode') == 'sudden' and summary.get('correct_count', 0) >= 5:
        try_unlock('survivor')

    if summary.get('mode') == 'daily':
        try_unlock('daily_agent')

    if (summary.get('level') == 'hard' and
            summary.get('lives_left', 0) >= 3 and
            summary.get('correct_count', 0) >= 10):
        try_unlock('hard_cleared')

    if summary.get('mode') == '2player':
        try_unlock('tag_team')

    return newly


def populate_achievements(grid_widget):
    """เติมข้อมูล Achievements ลงใน GridLayout"""
    from kivy.uix.label import Label
    from kivy.uix.boxlayout import BoxLayout
    from kivy.graphics import Color, RoundedRectangle
    from kivy.metrics import dp, sp

    grid_widget.clear_widgets()
    unlocked = _load_ach()

    for ach in ACHIEVEMENTS:
        is_unlocked = ach['id'] in unlocked

        row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None, height=dp(56),
            padding=dp(12), spacing=dp(8)
        )

        bg_color = (0.06, 0.28, 0.08, 0.88) if is_unlocked else (0.08, 0.08, 0.16, 0.70)
        with row.canvas.before:
            Color(*bg_color)
            row._bg = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(12)])
        row.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                 size=lambda w, v: setattr(w._bg, 'size', v))

        # ใช้ [OK] / [--] แทน emoji ล็อค/ปลด
        lock_text  = '[OK]' if is_unlocked else '[--]'
        lock_color = (0.3, 1, 0.4, 1) if is_unlocked else (0.4, 0.4, 0.5, 1)
        lock_lbl = Label(
            text=lock_text, font_name='Sarabun',
            font_size=sp(13), bold=is_unlocked,
            color=lock_color, size_hint_x=0.12
        )

        # ชื่อ Achievement — ใช้ icon ที่เป็น ASCII แล้ว
        name_color = (1, 1, 1, 1) if is_unlocked else (0.5, 0.5, 0.6, 1)
        name_lbl = Label(
            text=f'{ach["icon"]} {ach["name"]}',
            font_name='Sarabun', font_size=sp(15),
            bold=is_unlocked, color=name_color,
            halign='left', size_hint_x=0.50
        )

        # คำอธิบาย
        desc_color = (0.8, 0.95, 0.8, 1) if is_unlocked else (0.4, 0.4, 0.5, 1)
        desc_lbl = Label(
            text=ach['desc'],
            font_name='Sarabun', font_size=sp(12),
            color=desc_color, halign='right',
            size_hint_x=0.38
        )

        row.add_widget(lock_lbl)
        row.add_widget(name_lbl)
        row.add_widget(desc_lbl)
        grid_widget.add_widget(row)