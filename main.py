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

# Шаг 1: Получаем свежий Access Token по примеру с сайта Сбера
    oauth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    auth_key = os.getenv("GIGACHAT_TOKEN")
    if not auth_key:
        await update.message.reply_text("GIGACHAT_TOKEN не добавлен в Railway 😅")
        return

    oauth_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": "test-rq-12345",  # любое уникальное, можно менять на рандом
        "Authorization": f"Basic {auth_key}"  # именно так, Basic + ключ
    }

    oauth_data = "scope=GIGACHAT_API_PERS"

    try:
        oauth_response = requests.post(
            oauth_url,
            headers=oauth_headers,
            data=oauth_data,
            verify=False,
            timeout=15
        )

        if oauth_response.status_code != 200:
            await update.message.reply_text(f"Ошибка токена: {oauth_response.status_code} - {oauth_response.text}")
            return

        access_token = oauth_response.json()["access_token"]
        await update.message.reply_text("Токен получен! Генерю текст...")

        # Шаг 2: Генерируем текст песни
        chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        chat_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "RqUID": "test-rq-12345"
        }

        payload = {
            "model": "GigaChat:latest",
            "messages": [
                {"role": "system", "content": "Ты крутой русский автор песен. Пиши матерно, если тема требует, рифмуй жёстко, делай 2 куплета + припев."},
                {"role": "user", "content": f"Напиши текст песни на тему: {theme}. Сделай куплеты, припев. Потом дай промпт для музыки в @gusli_aibot."}
            ],
            "temperature": 0.9
        }

        response = requests.post(
            chat_url,
            json=payload,
            headers=chat_headers,
            verify=False,
            timeout=30
        )

        if response.status_code == 200:
            text = response.json()["choices"][0]["message"]["content"]
            await update.message.reply_text(f"Вот текст песни:\n\n{text}\n\nКидай промпт в @gusli_aibot или @easysongbot!")
        else:
            await update.message.reply_text(f"Ошибка генерации: {response.status_code} - {response.text}")

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
