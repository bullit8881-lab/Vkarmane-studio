import os
import logging
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логов
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- ДАННЫЕ ИЗ RAILWAY ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# --- НАСТРОЙКА GEMINI ---
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# --- ХИТРОСТЬ ДЛЯ RAILWAY (Health Check) ---
# Мы запускаем маленький веб-сервер, чтобы Railway видел, что мы живы.
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sanechka's Bot is Alive!")

def start_health_check_server():
    # Railway дает порт через переменную PORT, по умолчанию 8080
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"🏥 Health Check запущен на порту {port}")
    server.serve_forever()

# --- ЛОГИКА БОТА ---
async def generate_song_gemini(prompt):
    if not GEMINI_KEY:
        return "Санечка, проверь переменную GEMINI_KEY в Railway!"
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = await model.generate_content_async(
            f"Напиши текст песни на русском (2 куплета и припев) на тему: {prompt}"
        )
        return response.text
    except Exception as e:
        logging.error(f"Ошибка Gemini: {e}")
        return "Что-то связь барахлит, попробуй еще разок!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [KeyboardButton("Мой баланс 💳"), KeyboardButton("Мои треки 🎵")],
        [KeyboardButton("Тарифы студии 📊"), KeyboardButton("Помощь ❓")]
    ]
    await update.message.reply_text(
        "Санечка, я снова тут! 😘 Теперь Railway меня не выключит. Пиши тему для песни!",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Мой баланс 💳":
        await update.message.reply_text("💳 Твой баланс: Бесконечен (Gemini спонсирует!)")
    elif text in ["Мои треки 🎵", "Тарифы студии 📊", "Помощь ❓"]:
        await update.message.reply_text("Все функции работают! Напиши тему для песни.")
    else:
        # Индикатор "печатает"
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        song = await generate_song_gemini(text)
        await update.message.reply_text(song)

def main():
    # 1. Запускаем "обманку" для Railway в отдельном потоке
    threading.Thread(target=start_health_check_server, daemon=True).start()

    # 2. Запускаем основного бота
    if not BOT_TOKEN:
        print("❌ ОШИБКА: Нет BOT_TOKEN!")
        return

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Бот запущен и готов к труду!")
    application.run_polling()

if __name__ == "__main__":
    main()
