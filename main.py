import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Берём токен из переменных окружения Railway
TOKEN = os.getenv("BOT_TOKEN")

def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.message.reply_text("✅ Бот запущен и работает!")

def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.message.reply_text("Напиши /start")

def main():
    if not TOKEN:
        raise RuntimeError("❌ BOT_TOKEN не найден в переменных окружения")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    print("🤖 Bot started")

    application.run_polling()

if __name__ == "__main__":
    main()
