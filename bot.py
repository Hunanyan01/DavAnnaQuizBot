# DavAnnaQuizBot - Fully Integrated, Clean Version
import os
from dotenv import load_dotenv
load_dotenv()

import json
import random
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.error import TelegramError


# Config
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

#TOKEN = "7517138982:AAHBHT07jT9LUIAGum2JCzDkTgNCPFwErp8"  # ❌ Replace with your actual token!
QUESTIONS_FILE = "../.venv/questions.json"
PROGRESS_FILE = "../.venv/progress.json"
DAILY_LIMIT = 10
DAVID_ID = 1505441793
ANNA_ID = 1802076880

# External modules
from mod_hint import hint_command
from mod_store import (
    store_command, handle_store_purchase,
    my_items_command, anna_items_command,
    davit_items_command, both_items_command
)
from timed_questions import send_timed_question, cancel_timer, user_state
#from CallbackQueryHandler import button_handler
from utils import load_questions, load_progress, save_progress
from telegram import Update
from telegram.ext import ApplicationBuilder


# Load/save helpers
def load_questions():
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_progress():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Բարև ✨ Սա DavAnnaQuizBot-ն է։ Սեղմիր /next՝ ստանալու հարց։")

async def topic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = load_questions()
    topics = list(set(q["topic"] for q in questions))
    text = "📚 Հասանելի թեմաները：\n" + "\n".join(f"• {t}" for t in topics)
    await update.message.reply_text(text)

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    today = datetime.now().date().isoformat()
    questions = load_questions()
    progress = load_progress()

    if user_id not in progress:
        progress[user_id] = {"answered": [], "xp_used": 0, "purchases": []}
    user_data = progress[user_id]

    if user_data.get("date") != today:
        user_data["answered"] = []
        user_data["date"] = today
        user_data["count"] = 0

    if user_id in user_state:
        await update.message.reply_text("❗️ Նախ պատասխանիր ը ունցայիք հարցինքֈ")
        return

    if user_data.get("count", 0) >= DAILY_LIMIT:
        await update.message.reply_text("📋 Այսոր առդեն ստացել ես 10 հարցֈ")
        return

    unanswered = [q for q in questions if q["id"] not in user_data["answered"]]
    if not unanswered:
        await update.message.reply_text("✅ Առդեն պատասխանել ես բոլոր հարցերինֈ")
        return

    question = random.choice(unanswered)
    qid = question["id"]
    user_data["count"] += 1
    progress[user_id] = user_data
    save_progress(progress)

    keyboard = [
        [InlineKeyboardButton(f"{i + 1}. {opt}", callback_data=f"{qid}|{i + 1}")]
        for i, opt in enumerate(question["options"])
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    print("📤 Հարցը՝", question['question'])
    print("📦 Կոճակների keyboard =", keyboard)
    print("🎯 reply_markup =", reply_markup)

    await send_timed_question(update, context, question, timeout=20, reply_markup=reply_markup)

async def my_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    progress = load_progress()
    user_data = progress.get(user_id)

    if not user_data:
        await update.message.reply_text("❗️ Դեր հարց չես ստացելը")
        return

    total_correct = len(user_data.get("answered", []))
    xp = len(user_data.get("answered", [])) * 10 - user_data.get("xp_used", 0)
    level = xp // 50 + 1

    name = "Դավիթ" if int(user_id) == DAVID_ID else "Աննա" if int(user_id) == ANNA_ID else "Օգտատեր"
    await update.message.reply_text(
        f"👤 {name} — Քո վիջակագղությունները：\n✅ Ճիշտ պատասխանները： {total_correct}\n⭐ XP： {xp}\n🏅 Մակարդակ： {level}"
    )

async def general_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("store_mode"):
        await handle_store_purchase(update, context)
    else:
        await update.message.reply_text("⚠️ Այս պահին այս տեքստը չեմ կարող հասկանալ։")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    data = query.data  # օրինակ՝ "12|3"
    question_id, selected_index = map(int, data.split("|"))

    questions = load_questions()
    question = next((q for q in questions if q["id"] == question_id), None)

    if not question:
        await query.edit_message_text("❗️Հարցը չի գտնվել։")
        return

    correct_index = question["correct"]
    name = "Դավիթ" if int(user_id) == DAVID_ID else "Աննա"

    progress = load_progress()
    user_data = progress.setdefault(user_id, {"answered": [], "xp_used": 0, "purchases": []})

    if question_id not in user_data["answered"]:
        if selected_index == correct_index:
            user_data["answered"].append(question_id)
            await query.edit_message_text(f"✅ {name}, ապրես թագավոր 👑")
        else:
            await query.edit_message_text(
                f"❌ {name}, սխալ էր։ Ճիշտ պատասխանը՝ {correct_index}. {question['options'][correct_index-1]}"
            )

        save_progress(progress)

    if user_id in user_state:
        del user_state[user_id]

# Main
def main():
    env = os.getenv("ENV", "local")
    webhook_url = os.getenv("WEBHOOK_URL")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_question))
    app.add_handler(CommandHandler("myscore", my_score))
    app.add_handler(CommandHandler("store", store_command))
    app.add_handler(CommandHandler("myitems", my_items_command))
    app.add_handler(CommandHandler("anna_items", anna_items_command))
    app.add_handler(CommandHandler("davit_items", davit_items_command))
    app.add_handler(CommandHandler("items", both_items_command))
    app.add_handler(CommandHandler("hint", hint_command))
    app.add_handler(CommandHandler("topic", topic_command))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), general_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("DavAnnaQuizBot ✅ Աշխատում է Render-ում։")

    if env == "render":
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", 8000)),
            webhook_url=webhook_url
        )
    else:
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", 8443)),
            webhook_url=os.environ.get("WEBHOOK_URL")
        )


if __name__ == "__main__":
    main()
