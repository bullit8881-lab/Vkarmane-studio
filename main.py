import os
import requests
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = "8462140457:AAFLOvHcBvl2LSrKuO3lHCHWUR3a5yHz-LU"
OR_KEY = os.getenv("OPENROUTER_KEY")

def generate_song(prompt):
    if not OR_KEY:
        return "Ошибка: Проверь OPENROUTER_KEY в Railway!"
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OR_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://railway.app"
    }
    
    # Пробуем по очереди две разные бесплатные модели
    models = [
        "mistralai/mistral-7b-instruct:free",
        "huggingfaceh4/zephyr-7b-beta:free"
    ]
    
    for model in models:
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Ты профессиональный автор песен. Пиши на русском: 2 куплета и припев."},
                {"role": "user", "content": f"Напиши песню на тему: {prompt}"}
            ]
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            result = response.json()
            if 'choices' in result:
                return result['choices'][0]['message']['content']
        except:
            continue # Если модель подвела, пробуем следующую
            
    return "Санечка, все ИИ сейчас перегружены. Давай попробуем еще раз через минуту? Такое бывает с бесплатными лимитами."

def get_main_menu():
    keyboard = [
        [KeyboardButton("Мой баланс 💳"), KeyboardButton("Мои треки 🎵")],
        [KeyboardButton("Тарифы студии 📊"), KeyboardButton("Помощь ❓")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в Студию в кармане! 🎶\n\nТвои кнопки управления теперь внизу. Просто напиши тему для песни!",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Мой баланс 💳":
        await update.message.reply_text("💳 Твой баланс: **42 кристалла**.", parse_mode="Markdown")
    elif text == "Мои треки 🎵":
        await update.message.reply_text("🎵 Архив пока пуст. Но скоро здесь будут хиты!")
    elif text == "Тарифы студии 📊":
        await update.message.reply_text("📊 10 кристаллов — 500 руб.\nДля покупки: @AlexanderAnatolyevich")
    elif text == "Помощь ❓":
        await update.message.reply_text("❓ Просто напиши мне тему песни, и я приступлю!")
    else:
        wait_msg = await update.message.reply_text("🎸 Сочиняю хит для тебя...")
        song = generate_song(text)
        await wait_msg.edit_text(song)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
