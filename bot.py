import os
import threading
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer

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

keyboard = [["📖 Отправить цитату"]]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ─────────────────────────────
# 🔥 WEB SERVER (для Render)
# ─────────────────────────────
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ─────────────────────────────
# START
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

# ─────────────────────────────
# MAIN LOGIC
# ─────────────────────────────
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
# 🔥 УСТОЙЧИВЫЙ ЗАПУСК (ГЛАВНЫЙ ФИКС)
# ─────────────────────────────
async def run_bot():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    while True:
        try:
            print("Bot is running...")
            await app.run_polling(drop_pending_updates=True)
        except Exception as e:
            print(f"Ошибка: {e}")
            print("Перезапуск через 5 секунд...")
            await asyncio.sleep(5)

def main():
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()
