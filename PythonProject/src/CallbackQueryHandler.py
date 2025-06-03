from telegram import Update
from telegram.ext import ContextTypes

from telegram.ext import CallbackQueryHandler  # եթե սա պետք է

from utils import load_questions, load_progress, save_progress  # եթե այս ֆունկցիաները կան ուրիշ ֆայլում
from timed_questions import user_state  # եթե դա էլ պետք է

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    data = query.data  # օրինակ: "12|3"
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
