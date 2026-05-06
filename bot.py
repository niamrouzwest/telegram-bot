import os
from flask import Flask, request

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "8601228433:AAHcShB35RepfaLPyGU2y-thhDoCiWwH0PQ"
YOUR_CHAT_ID = 164564542

PORT = int(os.environ.get("PORT", 10000))

app_flask = Flask(__name__)

USER_STATE = {}

keyboard = [["📖 Отправить цитату"]]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ─────────────────────────────
# TELEGRAM LOGIC
# ─────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_STATE.pop(update.effective_user.id, None)

    await update.message.reply_text(
        "📖 Добро пожаловать в тихое место для слов - Цитаты недели\n"
        "📚 <a href='https://t.me/bombooklovers'>BOM: Booklovers Of Moldova</a>\n\n"
        "Здесь можно оставить цитату, которая зацепила, согрела или не отпускает.\n"
        "Нажми кнопку ниже ✍️",
        reply_markup=markup,
        parse_mode="HTML"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    state = USER_STATE.get(user_id)

    if state is None:
        if text == "📖 Отправить цитату":
            USER_STATE[user_id] = {"step": "quote"}
            await update.message.reply_text("Отправь цитату ✍️")
        else:
            await update.message.reply_text("Нажми кнопку 📖 «Отправить цитату»")
        return

    if state["step"] == "quote":
        USER_STATE[user_id]["quote"] = text
        USER_STATE[user_id]["step"] = "source"
        await update.message.reply_text("Из какой это книги? 📚")
        return

    if state["step"] == "source":
        quote = state.get("quote", "")
        source = text

        await context.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text=f"📩 Новая анонимная цитата:\n\n{quote}\n\n📚 {source}\n\n---"
        )

        await update.message.reply_text("Цитата отправлена ✨")

        USER_STATE.pop(user_id, None)

# ─────────────────────────────
# APP
# ─────────────────────────────
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ─────────────────────────────
# WEBHOOK SETUP (ПРАВИЛЬНЫЙ)
# ─────────────────────────────
@app_flask.route("/", methods=["GET"])
def home():
    return "Bot is running", 200


@app_flask.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok", 200

# ─────────────────────────────
# START
# ─────────────────────────────
if __name__ == "__main__":

    import asyncio

    async def main():
        await application.initialize()
        await application.start()

        await application.bot.set_webhook(
            url="https://telegram-bot-12cf.onrender.com/webhook"
        )

        app_flask.run(host="0.0.0.0", port=PORT)

    asyncio.run(main())
