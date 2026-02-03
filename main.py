import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование, чтобы видеть, если что-то пойдет не так
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Берем токен из переменных Railway (BOT_TOKEN)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Создаем меню с твоими разделами
def get_main_menu():
    keyboard = [
        [KeyboardButton("🎤 Студия (Песни для Машки)")],
        [KeyboardButton("🙏 Молитва (Для брата)")],
        [KeyboardButton("❓ Помощь / Инфо")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Привет, Санечка! 👋 (или гость студии {user_name})\n\n"
