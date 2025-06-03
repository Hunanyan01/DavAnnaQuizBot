# mod_hint.py
# 🧠 GPT Hint համակարգ Դավիթի և Աննայի համար

import openai
import json
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from timed_questions import user_state

PROGRESS_FILE = "../.venv/progress.json"
OPENAI_API_KEY = "7517138982:AAHBHT07jT9LUIAGum2JCzDkTgNCPFwErp8"  # ← այստեղ փոխիր API բանալին
XP_COST = 5  # Քանի XP պիտի հանվի hint-ի համար

openai.api_key = OPENAI_API_KEY

def load_progress():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

async def hint_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    question_data = user_state.get(user_id)

    if not question_data:
        await update.message.reply_text("⚠️ Սկզբում սեղմիր /next՝ հարց ստանալու համար։")
        return

    question = question_data.get("question") if isinstance(question_data, dict) else question_data
    if not question:
        await update.message.reply_text("⚠️ Չհաջողվեց գտնել ակտիվ հարց։")
        return

    progress = load_progress()
    user_data = progress.get(user_id, {"answered": [], "xp_used": 0, "count": 0, "date": datetime.now().date().isoformat()})

    earned_xp = len(user_data.get("answered", [])) * 10
    remaining_xp = earned_xp - user_data.get("xp_used", 0)

    if remaining_xp < XP_COST:
        await update.message.reply_text(f"😕 Քեզ անհրաժեշտ է առնվազն {XP_COST} XP՝ հուշում ստանալու համար։")
        return

    user_data["xp_used"] += XP_COST
    progress[user_id] = user_data
    save_progress(progress)

    prompt = f"Տվե՛ք հուշում այս հարցի համար, առանց ուղիղ պատասխան տալու։\n\nՀարցը՝ {question['question']}\nՏարբերակները՝ {question['options']}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Դու օգնող հայ ուսուցիչ ես։ Քո հուշումները խելացի, բայց չեզոք են։"},
                {"role": "user", "content": prompt}
            ]
        )
        hint = response["choices"][0]["message"]["content"]
        await update.message.reply_text(f"💡 Հուշում (✂️ {XP_COST} XP):\n{hint}")
    except Exception as e:
        await update.message.reply_text("😕 GPT հուշման համակարգը սխալ տվեց։ Ստուգիր API բանալին։")
        print("Hint Error:", e)
