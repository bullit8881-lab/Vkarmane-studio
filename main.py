import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Логи для отладки
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Токены из Railway Variables
TOKEN = os.getenv("BOT_TOKEN")
GIGACHAT_TOKEN = os.getenv("GIGACHAT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Дарова! Я умный Сонграйтер 🔥\n"
        "Напиши /song и тему песни, например:\n"
        "/song про кузнечиков в стиле шансон\n"
        "Или просто текст — отвечу эхом"
    )

async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напиши тему после /song, например:\n/song про усталость после завода в стиле русский рок")
        return

    theme = ' '.join(context.args)
    await update.message.reply_text(f"Генерю текст песни на тему '{theme}'... Подожди 10–20 сек...")

    if not GIGACHAT_TOKEN:
        await update.message.reply_text("GIGACHAT_TOKEN не добавлен в Variables Railway 😅 Добавь его!")
        return

    # Шаг 1: Получаем Access Token (по примеру Сбера)
    oauth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    oauth_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": "test-rq-2026",  # любое уникальное
        "Authorization": f"Basic {GIGACHAT_TOKEN}"
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
            await update.message.reply_text(f"Ошибка получения токена: {oauth_response.status_code}\n{oauth_response.text}")
            return

        access_token = oauth_response.json()["access_token"]
        await update.message.reply_text("Токен получен! Генерю текст...")

        # Шаг 2: Генерируем текст песни
        chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        chat_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "RqUID": "test-rq-2026"
        }

        payload = {
            "model": "GigaChat:latest",
            "messages": [
                {"role": "system", "content": "Ты крутой русский автор песен. Пиши матерно, если тема требует, рифмуй жёстко, делай 2 куплета + припев + бридж. В конце дай готовый промпт для @gusli_aibot или Suno."},
                {"role": "user", "content": f"Напиши текст песни на тему: {theme}. Сделай круто!"}
            ],
            "temperature": 0.9,
            "max_tokens": 800
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
            await update.message.reply_text(f"Вот текст песни:\n\n{text}\n\nТеперь вставь промпт в @gusli_aibot или @easysongbot и получи трек! 🔥")
        else:
            await update.message.reply_text(f"Ошибка генерации: {response.status_code}\n{response.text}")

    except Exception as e:
        await update.message.reply_text(f"Что-то сломалось: {str(e)}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Эхо: {update.message.text}")

def main():
    app = Application.builder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("song", song))

    # Эхо на всё остальное
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
