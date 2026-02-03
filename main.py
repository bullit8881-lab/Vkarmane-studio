import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("Создать песню 🎤")],
        [KeyboardButton("Тарифы 💰")],
        [KeyboardButton("Баланс 💳")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("Дарова! Выбери кнопку:", reply_markup=reply_markup)

async def create_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши тему песни (например: про кузнечиков в стиле шансон)")

async def tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("5 песен - 50 руб")],
        [KeyboardButton("Unlimited на месяц - 300 руб")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выбери тариф:", reply_markup=reply_markup)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Баланс пока 0 кредитов (скоро подключим оплату)")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Создать песню 🎤":
        await create_song(update, context)
    elif text == "Тарифы 💰":
        await tariffs(update, context)
    elif text == "Баланс 💳":
        await balance(update, context)
    elif text == "5 песен - 50 руб":
        await update.message.reply_text("Оплата 50 руб за 5 песен — скоро подключим реальную оплату!")
    elif text == "Unlimited на месяц - 300 руб":
        await update.message.reply_text("Оплата 300 руб за unlimited — скоро подключим!")
    else:
        await update.message.reply_text(f"Эхо: {text}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # Обработка всех текстовых сообщений и кнопок
    app.add_handler(MessageHandler(filters.TEXT, handle_button))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
