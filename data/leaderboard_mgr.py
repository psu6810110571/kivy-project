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