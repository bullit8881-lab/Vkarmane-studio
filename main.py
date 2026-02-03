import os
import requests
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

# ТОКЕНЫ
BOT_TOKEN = "8462140457:AAFLOvHcBvl2LSrKuO3lHCHWUR3a5yHz-LU"
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")

# Функция генерации через DeepSeek
def generate_song_deepseek(prompt):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_KEY}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты крутой автор песен. Пиши на русском языке (2 куплета и припев)."},
            {"role": "user", "content": f"Напиши песню на тему: {prompt}"}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Санечка, ИИ призадумался... Проверь ключ DeepSeek! (Ошибка: {e})"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Принудительно ставим меню
    commands = [
        BotCommand("start", "Запустить студию 🚀"),
        BotCommand("help", "Помощь и инфо ❓")
    ]
    await context.bot.set_my_commands(commands)
    await update.message.reply_text("Санечка, Студия готова! Напиши тему песни — и я создам хит! ✨")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    wait_msg = await update.message.reply_text("✍️ Пишу для тебя шедевр...")
    song_text = generate_song_deepseek(user_text)
    await wait_msg.edit_text(song_text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
