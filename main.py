import os
import requests
import logging
from telegram import Update, BotCommand, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Логирование
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ТОКЕНЫ
BOT_TOKEN = "8462140457:AAFLOvHcBvl2LSrKuO3lHCHWUR3a5yHz-LU"
OR_KEY = os.getenv("OPENROUTER_KEY")

# --- ГЕНЕРАЦИЯ ---
def generate_song(prompt):
    if not OR_KEY:
        return "Ошибка: В Railway не добавлен OPENROUTER_KEY!"
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OR_KEY}", "Content-Type": "application/json"}
    
    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "system", "content": "Ты профессиональный автор песен. Пиши на русском языке: 2 куплета и припев."},
            {"role": "user", "content": f"Напиши текст песни на тему: {prompt}"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=40)
        result = response.json()
        return result['choices'][0]['message']['content'] if 'choices' in result else "ИИ занят, попробуй еще раз!"
    except:
        return "Связь прервалась. Попробуй снова!"

# --- МЕНЮ КНОПОК ---
def get_main_menu():
    keyboard = [
        [KeyboardButton("Мой баланс 💳"), KeyboardButton("Мои треки 🎵")],
        [KeyboardButton("Тарифы студии 📊"), KeyboardButton("Помощь ❓")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- ОБРАБОТЧИКИ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Устанавливаем и скрытое меню, и видимые кнопки
    await update.message.reply_text(
        "Добро пожаловать в **Студию в кармане**! 🎶\n\nИспользуй кнопки ниже или просто напиши тему для песни.",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Мой баланс 💳":
        await update.message.reply_text("💳 Твой баланс: **42 кристалла**.", parse_mode="Markdown")
    elif text == "Мои треки 🎵":
        await update.message.reply_text("🎵 Архив пуст. Напиши свою первую песню!")
    elif text == "Тарифы студии 📊":
        await update.message.reply_text("📊 10 кристаллов — 500 руб. Для покупки: @AlexanderAnatolyevich")
    elif text == "Помощь ❓":
        await update.message.reply_text("❓ Просто отправь текст, и я напишу песню!")
    else:
        # Если это не кнопка, значит это тема для песни
        wait_msg = await update.message.reply_text("🎸 Сочиняю хит... Секундочку!")
        song = generate_song(text)
        await wait_msg.edit_text(song)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Студия с нижним меню запущена!")
    app.run_polling()

if __name__ == "__main__":
    main()
