# analyze.py
# 📊 DavAnna QuizBot վերլուծության համակարգ

import json
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

PROGRESS_FILE = "../.venv/progress.json"
DAVID_ID = 1505441793
ANNA_ID = 1802076880


def load_progress():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    progress = load_progress()
    now = datetime.now()
    week_ago = (now - timedelta(days=7)).date().isoformat()

    def score(user_id):
        data = progress.get(str(user_id), {})
        total = len(data.get("answered", []))
        last_week = 0
        if data.get("date") and data["date"] >= week_ago:
            last_week = data.get("count", 0)
        return total, last_week

    david_total, david_week = score(DAVID_ID)
    anna_total, anna_week = score(ANNA_ID)

    winner = "🤴 Դավիթ" if david_week > anna_week else "👸 Աննա" if anna_week > david_week else "🤝 Ոչ ոք (ոչ-ոքի)"

    text = f"📊 DavAnna QuizBot Վերլուծություն👑 Այս շաբաթ: Դավիթ — {david_week} հարց• Աննա — {anna_week} հարց📚 Ընդհանուր:• Դավիթ — {david_total} հարց• Աննա — {anna_total} հարց🏆 Հաղթող՝ {winner}! 💥"

    await update.message.reply_text(text)
