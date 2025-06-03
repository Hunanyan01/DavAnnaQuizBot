# mod_store.py
# 🛍️ XP Store համակարգ՝ Դավիթի ու Աննայի համար

import json
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

PROGRESS_FILE = "../.venv/progress.json"
DAVID_ID = 1505441793
ANNA_ID = 1802076880

STORE_ITEMS = [
    {"id": 1, "name": "👕 Շապիկ", "xp": 50},
    {"id": 2, "name": "🧦 Գուլպաներ", "xp": 10},
    {"id": 3, "name": "🧢 Գլխարկ", "xp": 80},
    {"id": 4, "name": "🐶 Շունիկ", "xp": 200},
    {"id": 5, "name": "🐱 Կատու", "xp": 190},
    {"id": 6, "name": "🎧 Ականջակալներ", "xp": 30},
    {"id": 7, "name": "📱 Հեռախոս", "xp": 190},
    {"id": 8, "name": "🏠 Տուն", "xp": 420},
    {"id": 9, "name": "🚗 Մեքենա", "xp": 300},
    {"id": 10, "name": "✈️ Ինքնաթիռ", "xp": 500},
    {"id": 11, "name": "💻 Նոթբուք", "xp": 80},
    {"id": 12, "name": "⌚️ Ժամացույց", "xp": 95},
    {"id": 13, "name": "📺 Հեռուստացույց", "xp": 110},
    {"id": 14, "name": "🛏️ Մահճակալ", "xp": 20},
    {"id": 15, "name": "🪑 Աթոռ", "xp": 35},
    {"id": 16, "name": "🖼️ Նկարչություն", "xp": 50},
    {"id": 17, "name": "🎸 Կիթառ", "xp": 65},
    {"id": 18, "name": "🎹 Դաշնամուր", "xp": 80},
    {"id": 19, "name": "🎮 Խաղային կոնսոլ", "xp": 95},
    {"id": 20, "name": "🧸 Խաղալիք արջուկ", "xp": 110}
]

STORE_ITEMS_DICT = {item["id"]: item for item in STORE_ITEMS}


def load_progress():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


async def store_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    progress = load_progress()
    user_data = progress.get(user_id, {"answered": [], "xp_used": 0, "purchases": []})

    total_xp = len(user_data["answered"]) * 10 - user_data.get("xp_used", 0)

    text = f"🛍️ Քո XP՝ {total_xp}\nՑանկանու՞մ ես ինչ-որ բան գնել:\n"
    for item_id in sorted(STORE_ITEMS_DICT):
        item = STORE_ITEMS_DICT[item_id]
        text += f"{item_id}. {item['name']} — {item['xp']} XP\n"
    text += "\n✏️ Պատասխանիր միայն թվով (օր.՝ 1)՝ գնելու համար։"

    progress[user_id] = user_data
    save_progress(progress)
    await update.message.reply_text(text)
    context.user_data["store_mode"] = True


async def handle_store_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("store_mode"):
        return

    user_id = str(update.effective_user.id)
    progress = load_progress()
    user_data = progress.get(user_id, {"answered": [], "xp_used": 0, "purchases": []})

    try:
        choice = int(update.message.text.strip())
    except:
        await update.message.reply_text("⚠️ Խնդրում ենք ուղարկել միայն թվով տարբերակ։")
        return

    if choice not in STORE_ITEMS_DICT:
        await update.message.reply_text("❌ Այդ տարբերակը չկա։")
        return

    item = STORE_ITEMS_DICT[choice]
    xp = len(user_data["answered"]) * 10 - user_data.get("xp_used", 0)

    if xp < item["xp"]:
        await update.message.reply_text("💸 Քեզ բավարար XP չկա այս իրի համար։")
        return

    user_data["purchases"].append(item["name"])
    user_data["xp_used"] += item["xp"]
    progress[user_id] = user_data
    save_progress(progress)

    context.user_data["store_mode"] = False
    await update.message.reply_text(f"✅ Գնել ես՝ {item['name']} ({item['xp']} XP)")


async def my_items_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    progress = load_progress()
    user_data = progress.get(user_id, {})
    items = user_data.get("purchases", [])

    if not items:
        await update.message.reply_text("📦 Դու դեռ ոչինչ չես գնել։")
    else:
        text = "🎁 Գնված իրեր՝\n" + "\n".join(f"• {item}" for item in items)
        await update.message.reply_text(text)


async def anna_items_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    progress = load_progress()
    user_data = progress.get(str(ANNA_ID), {})
    items = user_data.get("purchases", [])

    if not items:
        await update.message.reply_text("📦 Աննան դեռ ոչինչ չի գնել։")
    else:
        text = "🎀 Աննայի գնած իրերը՝\n" + "\n".join(f"• {item}" for item in items)
        await update.message.reply_text(text)


async def davit_items_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    progress = load_progress()
    user_data = progress.get(str(DAVID_ID), {})
    items = user_data.get("purchases", [])

    if not items:
        await update.message.reply_text("📦 Դավիթը դեռ ոչինչ չի գնել։")
    else:
        text = "👑 Դավիթի գնած իրերը՝\n" + "\n".join(f"• {item}" for item in items)
        await update.message.reply_text(text)


async def both_items_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    progress = load_progress()
    david_data = progress.get(str(DAVID_ID), {})
    anna_data = progress.get(str(ANNA_ID), {})

    david_items = david_data.get("purchases", [])
    anna_items = anna_data.get("purchases", [])

    text = "🛍️ Դավիթի և Աննայի գնումները\n\n"
    text += "👑 Դավիթ\n"
    text += "\n".join(f"• {item}" for item in david_items) if david_items else "— Չի գնել ոչինչ։"
    text += "\n\n🎀 Աննա\n"
    text += "\n".join(f"• {item}" for item in anna_items) if anna_items else "— Չի գնել ոչինչ։"

    await update.message.reply_text(text)
