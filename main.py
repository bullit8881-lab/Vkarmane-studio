import os
import logging
import google.generativeai as genai
from telegram import Update, LabeledPrice
from telegram.ext import Application, CommandHandler, MessageHandler, filters, PreCheckoutQueryHandler, ContextTypes

# Настройка логов
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# ТОКЕНЫ
BOT_TOKEN = "8462140457:AAFLOvHcBvl2LSrKuO3lHCHWUR3a5yHz-LU"
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Настройка Gemini
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')

# Функция генерации через официальную библиотеку
async def generate_song_ai(prompt):
    try:
        response = model.generate_content(
            f"Ты профессиональный автор песен. Напиши текст песни (2 куплета и припев) на тему: {prompt}. "
            f"В конце добавь промпт для музыкальной нейросети на английском."
        )
        return response.text
    except Exception as e:
        logging.error(f"Ошибка Gemini: {e}")
        return "Санечка, сервер Google вредничает. Проверь, привязан ли ключ в Railway Variables!"

# --- ЛОГИКА БОТА ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Студия готова к хитам! 🚀\nНапиши тему песни или используй /buy")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    status_msg = await update.message.reply_text("✨ Творю магию... подожди чуток...")
    
    result = await generate_song_ai(user_text)
    await status_msg.edit_text(result)

# --- ПЛАТЕЖИ ---
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = [LabeledPrice("10 Кристаллов", 500 * 100)]
    await context.bot.send_invoice(
        update.message.chat_id, "Пополнение", "10 кристаллов",
        "payload", PAYMENT_TOKEN, "RUB", prices
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(PreCheckoutQueryHandler(lambda u, c: u.pre_checkout_query.answer(ok=True)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()
