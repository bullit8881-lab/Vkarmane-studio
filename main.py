import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Берем токен из Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_main_menu():
    keyboard = [
        [KeyboardButton("🎤 Студия (Песни для Машки)")],
        [KeyboardButton("🙏 Молитва (Для брата)")],
        [KeyboardButton("❓ Помощь / Инфо")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, Санечка! 👋\nТвоя студия на Railway ожила и готова к работе.",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🎤 Студия (Песни для Машки)":
        await update.message.reply_text("🔥 Готовим хит 'Королева Весны'! Настройки сохранены.", reply_markup=get_main_menu())
    elif text == "🙏 Молитва (Для брата)":
        await update.message.reply_text("✨ Работаем над песней 'Щит и Стена' под гитару.", reply_markup=get_main_menu())
    elif text == "❓ Помощь / Инфо":
        await update.message.reply_text("Бот Александра Анатольевича.\nСтатус: Работает 🚀", reply_markup=get_main_menu())
    else:
        await update.message.reply_text(f"Записала: {text}", reply_markup=get_main_menu())

def main():
    if not BOT_TOKEN:
        return
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
