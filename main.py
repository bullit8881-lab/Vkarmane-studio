import logging
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

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
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("5 песен - 50 руб", callback_data="pay_5")],
        [InlineKeyboardButton("Unlimited на месяц - 300 руб", callback_data="pay_unlimited")]
    ])
    await update.message.reply_text("Выбери тариф:", reply_markup=keyboard)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Баланс пока 0 кредитов (скоро подключим оплату)")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "pay_5":
        await query.edit_message_text("Оплата 5 песен (50 руб) — скоро подключим реальную оплату!")
    elif query.data == "pay_unlimited":
        await query.edit_message_text("Оплата Unlimited (300 руб) — скоро подключим реальную оплату!")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Создать песню 🎤":
        await create_song(update, context)
    elif text == "Тарифы 💰":
        await tariffs(update, context)
    elif text == "Баланс 💳":
        await balance(update, context)
    else:
        await update.message.reply_text(f"Эхо: {text}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    # Обработка кнопок и текста
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
