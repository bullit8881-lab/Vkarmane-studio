import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Бот запущен и работает!")


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong!")


def main():
    if not TOKEN:
        raise RuntimeError("❌ BOT_TOKEN не найден в переменных окружения")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))

    print("✅ Bot started")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
