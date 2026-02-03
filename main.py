import os
import requests
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логов
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- ДАННЫЕ ИЗ RAILWAY ---
BOT_TOKEN = "8462140457:AAFLOvHcBvl2LSrKuO3lHCHWUR3a5yHz-LU"
# Берем именно тот ключ, который ты добавил в переменные
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- ФУНКЦИЯ ГЕНЕРАЦИИ ПЕСНИ (DeepSeek) ---
def generate_song(prompt):
    if not DEEPSEEK_KEY:
        return "Ошибка: В Railway не найден DEEPSEEK_API_KEY! Проверь вкладку Variables."
    
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты профессиональный поэт и автор песен. Пиши на русском языке: 2 куплета и припев."},
            {"role": "user", "content": f"Напиши текст песни на тему: {prompt}"}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=40)
        result = response.json()
        
        if 'choices' in result:
            return result['choices'][0]['message']['content']
        else:
            error_info = result.get('error', {}).get('message', 'Неизвестная ошибка API')
            return f"Санечка, DeepSeek призадумался: {error_info}"
            
    except Exception as e:
        logging.error(f"Ошибка DeepSeek: {e}")
        return "Связь со студией DeepSeek прервалась. Попробуй еще раз через минуту!"

# --- КНОПКИ МЕНЮ ---
def get_main_menu():
    keyboard = [
        [KeyboardButton("Мой баланс 💳"), KeyboardButton("Мои треки 🎵")],
        [KeyboardButton("Тарифы студии 📊"), KeyboardButton("Помощь ❓")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- ОБРАБОТЧИКИ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Санечка, Студия в кармане на базе DeepSeek готова к работе! 🎶✨\n\nТвои кнопки управления внизу. Напиши тему для нового хита!",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Логика кнопок
    if text == "Мой баланс 💳":
        await update.message.reply_text("💳 Твой текущий баланс: **42 кристалла**.", parse_mode="Markdown")
    elif text == "Мои треки 🎵":
        await update.message.reply_text("🎵 Архив пока пуст. Давай напишем что-нибудь классное прямо сейчас?")
    elif text == "Тарифы студии 📊":
        tariffs = (
            "📊 **Тарифы нашей студии:**\n\n"
            "🔹 10 кристаллов — 500 руб.\n"
            "🔹 50 кристаллов — 2000 руб.\n"
            "🔹 Безлимит на день — 1000 руб.\n\n"
            "Для пополнения: @AlexanderAnatolyevich"
        )
        await update.message.reply_text(tariffs, parse_mode="Markdown")
    elif text == "Помощь ❓":
        await update.message.reply_text("❓ Все просто: отправь мне любую идею для песни, и я напишу текст в течение минуты.")
    else:
        # Генерация песни
        wait_msg = await update.message.reply_text("🎸 Санечка, DeepSeek подбирает рифмы... Секундочку!")
        song_result = generate_song(text)
        await wait_msg.edit_text(song_result)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Студия Санечки на DeepSeek запущена!")
    application.run_polling()

if __name__ == "__main__":
    main()
