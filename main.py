import os
import requests
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Логирование
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ТВОИ ДАННЫЕ
BOT_TOKEN = "8462140457:AAFLOvHcBvl2LSrKuO3lHCHWUR3a5yHz-LU"
OR_KEY = os.getenv("OPENROUTER_KEY")

# --- ФУНКЦИЯ ИИ (Сонграйтер) ---
def generate_song(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OR_KEY}",
        "Content-Type": "application/json"
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
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Санечка, ИИ призадумался... Ошибка: {e}"

# --- ОБРАБОТЧИКИ КОМАНД ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Установка синего меню принудительно
    commands = [
        BotCommand("start", "Запустить студию 🚀"),
        BotCommand("balance", "Мой баланс 💳"),
        BotCommand("music", "Мои треки 🎵"),
        BotCommand("tariffs", "Тарифы студии 📊"),
        BotCommand("help", "Помощь и инфо ❓")
    ]
    await context.bot.set_my_commands(commands)
    await update.message.reply_text("Санечка, добро пожаловать в 'Студию в кармане'! ✨\nНапиши мне тему для песни, и я начну творить.")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Пока база данных не подключена, выводим твои 42 кристалла
    await update.message.reply_text("💳 Твой баланс: **42 кристалла**.\nЭтого хватит на 42 шедевра! 🔥")

async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Твой архив треков пока пуст, но это ненадолго! Напиши свою первую песню прямо сейчас.")

async def tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📊 **Тарифы нашей студии:**\n\n"
        "🔹 10 кристаллов — 500 руб.\n"
        "🔹 50 кристаллов — 2000 руб.\n"
        "🔹 Безлимит на день — 1000 руб.\n\n"
        "Для пополнения пиши @AlexanderAnatolyevich"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Все просто: отправь мне любую тему (например: 'Песня про закат в Москве'), и я напишу текст и промпт для музыки!")

# --- ОБРАБОТКА ТЕКСТА ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    wait_msg = await update.message.reply_text("🎸 Санечка, настраиваю гитару... Пишу текст!")
    
    song_text = generate_song(user_text)
    await wait_msg.edit_text(song_text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем все функции
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("music", music))
    app.add_handler(CommandHandler("tariffs", tariffs))
    app.add_handler(CommandHandler("help", help_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Студия Санечки запущена!")
    app.run_polling()

if __name__ == "__main__":
    main()
