import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
GIGACHAT_TOKEN = os.getenv("GIGACHAT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Дарова! Я теперь умный! Напиши /song и тему песни, например:\n/song про кузнечиков в стиле рэп")

async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напиши тему после /song, например /song про усталость после завода")
        return

    theme = ' '.join(context.args)
    await update.message.reply_text(f"Генерю текст на тему '{theme}'... Подожди 10 сек...")

    if not GIGACHAT_TOKEN:
        await update.message.reply_text("Токен GigaChat не добавлен в Railway 😅 Добавь его в Variables")
        return

    headers = {
        "Authorization": f"Bearer {GIGACHAT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "GigaChat:latest",
        "messages": [
            {"role": "system", "content": "Ты крутой русский автор песен. Пиши матерно, если тема требует, рифмуй жёстко, делай 2 куплета + припев."},
            {"role": "user", "content": f"Напиши текст песни на тему: {theme}. Сделай куплеты, припев. Потом дай промпт для музыки в @gusli_aibot."}
        ],
        "temperature": 0.9
    }

    try:
        response = requests.post("https://gigachat.devices.sberbank.ru/api/v1/chat/completions", json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            text = response.json()["choices"][0]["message"]["content"]
            await update.message.reply_text(f"Вот текст песни:\n\n{text}\n\nТеперь вставь промпт в @gusli_aibot или @easysongbot и получи трек!")
        else:
            await update.message.reply_text(f"Ошибка: {response.status_code} - {response.text}")
    except Exception as e:
        await update.message.reply_text(f"Что-то сломалось: {str(e)}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Эхо: {update.message.text}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("song", song))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
