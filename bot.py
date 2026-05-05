import os
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
# START
# ─────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "📖 Добро пожаловать в тихое место для слов - Цитаты недели📚BOM: Booklovers Of Moldova\n\n"
        "Здесь можно оставить цитату, которая зацепила, согрела или не отпускает.\n"
        "Нажми кнопку ниже ✍️",
        reply_markup=markup
    )

# ─────────────────────────────
# MAIN LOGIC
# ─────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    step = context.user_data.get("step")

    # 🔒 1. ЕСЛИ СЦЕНАРИЙ НЕ НАЧАТ — ИГНОР ВСЕГО
    if step is None:
        if text == "📖 Отправить цитату":
            context.user_data["step"] = "quote"
            await update.message.reply_text("Отправь цитату ✍️")
        else:
            await update.message.reply_text("Нажми кнопку 📖 «Отправить цитату»")
        return

    # ✍️ 2. ПОЛУЧАЕМ ЦИТАТУ
    if step == "quote":
        if not text or not text.strip():
            return

        context.user_data["quote_text"] = text.strip()
        context.user_data["step"] = "source"

        await update.message.reply_text("Из какой это книги? 📚")
        return

    # 📚 3. ПОЛУЧАЕМ КНИГУ И ОТПРАВЛЯЕМ
    if step == "source":
        source = text.strip()
        quote = context.user_data.get("quote_text", "")

        await context.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text=f"📩 Новая анонимная цитата:\n\n{quote}\n\n📚 {source}\n\n---"
        )

        await update.message.reply_text("Цитата отправлена ✨")

        # 🔄 сброс состояния
        context.user_data.clear()

# ─────────────────────────────
# MAIN
# ─────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
