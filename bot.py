import os
from flask import Flask, request

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ───────────── ENV ─────────────
TOKEN = os.environ["BOT_TOKEN"]
YOUR_CHAT_ID = int(os.environ["CHAT_ID"])
BASE_URL = os.environ["BASE_URL"]

PORT = int(os.environ.get("PORT", 10000))

# ───────────── STATE ─────────────
USER_STATE = {}

# ───────────── UI ─────────────
keyboard = [["📖 Отправить цитату"]]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ───────────── APP ─────────────
app_flask = Flask(__name__)

application = Application.builder().token(TOKEN).build()


# ───────────── BOT LOGIC ─────────────
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
            await update.message.reply_text(
                "Чтобы отправить цитату, нажми кнопку 📖 «Отправить цитату»",
                reply_markup=markup
            )
        return

    if state.get("step") == "quote":
        USER_STATE[user_id]["quote"] = text
        USER_STATE[user_id]["step"] = "source"
        await update.message.reply_text("Из какой книги? 📚")
        return

    if state.get("step") == "source":
        quote = state.get("quote", "")
        source = text

        await context.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text=f"📩 Новая цитата:\n\n{quote}\n\n📚 {source}"
        )

        await update.message.reply_text("Цитата отправлена ✨")
        USER_STATE.pop(user_id, None)


# ───────────── HANDLERS ─────────────
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# ───────────── WEBHOOK ROUTE ─────────────
@app_flask.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)

        application.update_queue.put_nowait(update)

        return "ok", 200

    except Exception as e:
        print("WEBHOOK ERROR:", repr(e))
        return "error", 500


@app_flask.route("/", methods=["GET"])
def home():
    return "Bot is running", 200


# ───────────── STARTUP ─────────────
async def setup():
    await application.initialize()
    await application.start()

    await application.bot.set_webhook(f"{BASE_URL}/webhook")


if __name__ == "__main__":
    import asyncio

    asyncio.run(setup())

    app_flask.run(host="0.0.0.0", port=PORT)
