import json
import os

# ══════════════════════════════════════════════════════════════════════════════
#  leaderboard_mgr.py  —  จัดการ Leaderboard และ Achievements
# ══════════════════════════════════════════════════════════════════════════════

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
LB_FILE         = os.path.join(BASE_DIR, '..', 'leaderboard.json')
ACH_FILE        = os.path.join(BASE_DIR, '..', 'achievements.json')
MAX_ENTRIES     = 20

# ─── นิยาม Achievements ────────────────────────────────────────────────────────
ACHIEVEMENTS = [
    {"id": "first_blood",  "icon": "🩸", "name": "First Blood",  "desc": "เล่นครั้งแรก"},
    {"id": "on_fire",      "icon": "🔥", "name": "On Fire",      "desc": "Combo ×5 ขึ้นไป"},
    {"id": "perfect",      "icon": "⭐", "name": "Perfect",      "desc": "ตอบถูกทุกข้อใน 1 เกม"},
    {"id": "speedster",    "icon": "⚡", "name": "Speedster",    "desc": "ตอบถูกภายใน 2 วินาที"},
    {"id": "survivor",     "icon": "💀", "name": "Survivor",     "desc": "เล่น Sudden Death ผ่าน 5 ข้อ"},
    {"id": "daily_agent",  "icon": "📅", "name": "Daily Agent",  "desc": "ทำ Daily Challenge สำเร็จ"},
    {"id": "hard_cleared", "icon": "🔴", "name": "Hard Cleared", "desc": "ผ่าน Hard โดยไม่เสียชีวิต"},
    {"id": "boss_slayer",  "icon": "👹", "name": "Boss Slayer",  "desc": "ผ่าน Boss Round สำเร็จ"},
    {"id": "tag_team",     "icon": "👥", "name": "Tag Team",     "desc": "ชนะโหมด 2 ผู้เล่น"},
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
    print(f"[LB] saved: {name} → {score} pts ({category}/{level})")

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