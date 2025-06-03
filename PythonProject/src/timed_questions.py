import asyncio
from telegram import Update
from telegram.ext import ContextTypes

user_state = {}

async def send_timed_question(update: Update, context: ContextTypes.DEFAULT_TYPE, question: dict, timeout: int = 20, reply_markup=None):
    user_id = str(update.effective_user.id)

    old_text = f"🕒 Ունես {timeout} վայրկյան պատասխանիր.\n\n❓ {question['question']}"

    new_text = f"""❓ <b>{question['question']}</b>

1️⃣ {question['options'][0]}
2️⃣ {question['options'][1]}
3️⃣ {question['options'][2]}
4️⃣ {question['options'][3]}

🕒 Ունես {timeout} վայրկյան պատասխանիր։
"""

    if reply_markup:
        msg = await update.message.reply_text(
            new_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        print("⚠️ reply_markup = None, ուղարկվում է առանց կոճակների")  # ❗️
        msg = await update.message.reply_text(old_text)

    async def timeout_handler():
        try:
            await context.bot.send_message(...)
        except telegram.error.TimedOut:
            print("⚠️ Timeout է տեղի ունեցել։ Message չհասավ։")
        if user_id in user_state and user_state[user_id]["question"]["id"] == question["id"]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⏰ Ժամանակը սպառվեց։ Հաջորդ հարցը ստանալու համար գրիր /next։"
            )
            user_state.pop(user_id)

    task = asyncio.create_task(timeout_handler())

    user_state[user_id] = {
        "question": question,
        "message_id": msg.message_id,
        "timer_task": task
    }

# ✅ Ավելացրու սա
def cancel_timer(user_id: str):
    if user_id in user_state and user_state[user_id].get("timer_task"):
        user_state[user_id]["timer_task"].cancel()
