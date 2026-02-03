import os
import requests
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8462140457:AAFLOvHcBvl2LSrKuO3lHCHWUR3a5yHz-LU"
# Берем ключ именно из переменных Railway
OR_KEY = os.getenv("OPENROUTER_KEY")

def generate_song(prompt):
    if not OR_KEY:
        return "Санечка, в Railway не добавлен OPENROUTER_KEY! Добавь его в Variables."
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OR_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://railway.app", # Обязательно для OpenRouter
    }
    data = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {"role": "system", "content": "Ты профессиональный автор песен. Пиши на русском языке: 2 куплета и припев."},
            {"role": "user", "content": f"Напиши песню на тему: {prompt}"}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        if 'choices' in result:
            return result['choices'][0]['message']['content']
        else:
            return f"Ошибка API: {result.get('error', {}).get('message', 'Неизвестная ошибка')}"
    except Exception as e:
        return f"Связь оборвалась: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Принудительно ставим меню при старте
    commands = [
        BotCommand("start", "Запустить студию 🚀"),
        BotCommand("balance", "Мой баланс 💳"),
        BotCommand("music", "Мои треки 🎵"),
        BotCommand("tariffs", "Тарифы студии 📊"),
        BotCommand("help", "Помощь и инфо ❓")
    ]
    await context.bot.set_my_commands(commands)
    await update.message.reply_text("Санечка, Студия готова! Теперь и меню должно появиться. Жду твою тему для хита!")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💳 Твой баланс: 42 кристалла.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wait_msg = await update.message.reply_text("🎸 Пишу для тебя шедевр...")
    song_text = generate_song(update.message.text)
    await wait_msg.edit_text(song_text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
