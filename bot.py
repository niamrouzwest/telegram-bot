import os
import threading
from flask import Flask, request

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8601228433:AAHcShB35RepfaLPyGU2y-thhDoCiWwH0PQ"
YOUR_CHAT_ID = 164564542

PORT = int(os.environ.get("PORT", 10000))

app = Flask(__name__)

USER_STATE = {}

keyboard = [["📖 Отправить цитату"]]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ───────────── Telegram logic ─────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_STATE.pop(update.effective_user.id, None)

    await update.message.reply_text(
        "📖 Добро пожаловать в тихое место для слов - Цитаты недели\n"
        "📚 <a href='https://t.me/bombooklovers'>BOM: Booklovers Of Moldova</a>\n\n"
        "Здесь можно оставить цитату, которая зацепила, согрела или не отпускает.\n"
        "Нажми кнопку ниже ✍️",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    state = USER_STATE.get(user_id)

    if state is None:
        if text == "📖 Отправить цитату":
            USER_STATE[user_id] = {"step": "quote"}
            await update.message.reply_text("Отправь цитату ✍️")
        return

    if state["step"] == "quote":
        USER_STATE[user_id]["quote"] = text
        USER_STATE[user_id]["step"] = "source"
        await update.message.reply_text("Из какой это книги? 📚")
        return

    if state["step"] == "source":
        quote = state["quote"]
        source = text

        await context.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text=f"{quote}\n\n📚 {source}"
        )

        await update.message.reply_text("Готово ✨")
        USER_STATE.pop(user_id, None)

# ───────────── Application ─────────────

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ───────────── WEB SERVER (ВАЖНО) ─────────────

@app.route("/", methods=["GET"])
def home():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

# ───────────── START ─────────────

def run_bot():
    application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()

    app.run(host="0.0.0.0", port=PORT)
