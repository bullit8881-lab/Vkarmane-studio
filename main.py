import logging
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, PreCheckoutQueryHandler, CallbackQueryHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")

# Простой "баланс" юзеров (в реале используй DB, пока словарь)
user_balances = {}  # {user_id: credits}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = [
        [KeyboardButton("Создать песню 🎤")],
        [KeyboardButton("Тарифы 💰")],
        [KeyboardButton("Баланс 💳")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Дарова! Выбери кнопку:", reply_markup=reply_markup)

async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balance = user_balances.get(user_id, 0)
    if balance < 1:
        await update.message.reply_text("У тебя 0 кредитов. Купи тариф через 'Тарифы'!")
        return

    if not context.args:
        await update.message.reply_text("Напиши тему после /song, например /song про кузнечиков в стиле шансон")
        return

    theme = ' '.join(context.args)
    await update.message.reply_text(f"Генерю песню на тему '{theme}'... Подожди 10 сек... Трачу 1 кредит.")

    # Генерация от Grok (я сам)
    generated_text = f"Текст песни на тему '{theme}':\n\nКуплет 1:...\nПрипев:...\n(реальный текст от Grok)\n\nПромпт: 'песня в стиле шансон, текст: [текст]'"

    user_balances[user_id] = balance - 1
    await update.message.reply_text(generated_text)

async def tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("5 песен - 50 руб", callback_data="pay_5")],
        [InlineKeyboardButton("Unlimited на месяц - 300 руб", callback_data="pay_unlimited")]
    ])
    await update.message.reply_text("Выбери тариф:", reply_markup=keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "pay_5":
        await context.bot.send_invoice(
            chat_id=user_id,
            title="5 песен",
            description="5 кредитов на песни",
            payload="pay_5",
            provider_token=PAYMENT_TOKEN,
            currency="RUB",
            prices=[{"label": "5 песен", "amount": 5000}]  # 50 руб = 5000 копеек
        )
    elif query.data = "pay_unlimited":
        await context.bot.send_invoice(
            chat_id=user_id,
            title="Unlimited на месяц",
            description="Неограниченные песни на 30 дней",
            payload="pay_unlimited",
            provider_token=PAYMENT_TOKEN,
            currency="RUB",
            prices=[{"label": "Unlimited", "amount": 30000}]  # 300 руб = 30000 копеек
        )

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    payload = update.message.successful_payment.payload
    if payload == "pay_5":
        user_balances[user_id] = user_balances.get(user_id, 0) + 5
        await update.message.reply_text("Спасибо! +5 кредитов на балансе.")
    elif payload == "pay_unlimited":
        user_balances[user_id] = user_balances.get(user_id, 0) + 1000  # условно unlimited
        await update.message.reply_text("Спасибо! Unlimited на месяц активирован.")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = user_balances.get(user_id, 0)
    await update.message.reply_text(f"Твой баланс: {bal} кредитов")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Эхо: {update.message.text}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("song", song))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
