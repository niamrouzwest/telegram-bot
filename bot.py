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

# Render даёт порт через переменную окружения
PORT = int(os.environ.get("PORT", 10000))

app_flask = Flask(__name__)

keyboard = [["📖 Отправить цитату"]]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ─────────────────────────────
# TELEGRAM LOGIC
# ─────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "📖 Добро пожаловать в тихое место для слов - Цитаты недели\n"
        "📚 <a href='https://t.me/bombooklovers'>BOM: Booklovers Of Moldova</a>\n\n"
        "Здесь можно оставить цитату, которая зацепила, согрела или не отпускает.\n"
        "Нажми кнопку ниже ✍️",
        reply_markup=markup,
        parse_mode="HTML"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    step = context.user_data.get("step")

    if step is None:
        if text == "📖 Отправить цитату":
            context.user_data["step"] = "quote"
            await update.message.reply_text("Отправь цитату ✍️")
        else:
            await update.message.reply_text("Нажми кнопку 📖 «Отправить цитату»")
        return

    if step == "quote":
        if not text.strip():
            return
        context.user_data["quote_text"] = text.strip()
        context.user_data["step"] = "source"
        await update.message.reply_text("Из какой это книги? 📚")
        return

    if step == "source":
        quote = context.user_data.get("quote_text", "")
        source = text.strip()

        await context.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text=f"📩 Новая анонимная цитата:\n\n{quote}\n\n📚 {source}\n\n---"
        )

        await update.message.reply_text("Цитата отправлена ✨")
        context.user_data.clear()

# ─────────────────────────────
# TELEGRAM APP
# ─────────────────────────────
application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ─────────────────────────────
# WEBHOOK ROUTES
# ─────────────────────────────
@app_flask.route("/", methods=["GET"])
def home():
    return "Bot is running", 200

@app_flask.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

# ─────────────────────────────
# START
# ─────────────────────────────
if __name__ == "__main__":
    import asyncio

    async def setup():
        await application.initialize()
        await application.start()

    asyncio.run(setup())

    app_flask.run(host="0.0.0.0", port=PORT)
