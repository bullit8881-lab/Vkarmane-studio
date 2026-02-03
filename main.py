import os
import requests
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

# ТВОЙ ТОКЕН ТЕЛЕГРАМ
BOT_TOKEN = "8462140457:AAFLOvHcBvl2LSrKuO3lHCHWUR3a5yHz-LU"

# Функция генерации (используем бесплатный шлюз к Llama 3)
def generate_song(prompt):
    url = "https://ollama-api.extralabs.tech/v1/chat/completions" # Публичный шлюз
    data = {
        "model": "llama3",
        "messages": [
            {"role": "system", "content": "Ты профессиональный поэт. Пиши красивые песни на русском языке (2 куплета и припев)."},
            {"role": "user", "content": f"Напиши песню на тему: {prompt}"}
        ]
    }
    try:
        # Пытаемся получить ответ (без ключа, через открытый шлюз)
        response = requests.post(url, json=data, timeout=30)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return "Санечка, ИИ сегодня отдыхает. Напиши тему еще раз, я попробую пробиться!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ПРИНУДИТЕЛЬНО возвращаем синюю кнопку Меню
    commands = [
        BotCommand("start", "Запустить студию 🚀"),
        BotCommand("help", "Помощь ❓")
    ]
    await context.bot.set_my_commands(commands)
    await update.message.reply_text("Санечка, Студия в кармане открыта! ✨\nМеню должно появиться слева. Напиши тему для новой песни!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если юзер просто пишет текст - генерируем песню
    user_text = update.message.text
    wait_msg = await update.message.reply_text("🎸 Настраиваю гитару, пишу текст... Подожди немного.")
    
    song_text = generate_song(user_text)
    await wait_msg.edit_text(song_text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот Санечки запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
