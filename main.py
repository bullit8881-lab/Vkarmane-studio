import os
import requests
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логов, чтобы видеть, если что-то пойдет не так
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ТВОЙ ТОКЕН ТЕЛЕГРАМ (Оставляем как есть)
BOT_TOKEN = "8462140457:AAFLOvHcBvl2LSrKuO3lHCHWUR3a5yHz-LU"

# Функция генерации (Llama 3 через бесплатный шлюз)
def generate_song(prompt):
    url = "https://ollama-api.extralabs.tech/v1/chat/completions"
    data = {
        "model": "llama3",
        "messages": [
            {"role": "system", "content": "Ты профессиональный автор песен. Пиши на русском языке: 2 куплета и припев."},
            {"role": "user", "content": f"Напиши текст песни на тему: {prompt}"}
        ]
    }
    try:
        response = requests.post(url, json=data, timeout=40)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Ошибка ИИ: {e}")
        return "Санечка, связь с ИИ немного барахлит. Попробуй еще раз через минуту, я обязательно напишу!"

# Команда /start - она же включает СИНЮЮ КНОПКУ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Регистрируем команды в меню Telegram
    commands = [
        BotCommand("start", "Запустить студию 🚀"),
        BotCommand("help", "Как это работает? ❓")
    ]
    await context.bot.set_my_commands(commands)
    await update.message.reply_text("Санечка, Студия запущена! ✨\n\nТеперь у тебя должна появиться синяя кнопка 'Меню'. Просто напиши мне тему песни, и я приступлю к работе!")

# Обработка любого входящего текста
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # Небольшое уведомление, чтобы пользователь не скучал
    wait_msg = await update.message.reply_text("✍️ Подбираю рифмы, настраиваю инструменты... Секундочку!")
    
    song_result = generate_song(user_text)
    await wait_msg.edit_text(song_result)

def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Бот Санечки запущен и готов к работе!")
    application.run_polling()

if __name__ == "__main__":
    main()
