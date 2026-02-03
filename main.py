import logging
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set!")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL not set!")

WEBHOOK_PATH = "/webhook"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Дарова, {user.mention_html()}! Я Сонграйтер 🔥\n"
        "Кидай тему песни: 'про кузнечиков в стиле рэп'\n"
        "Команды: /music — тест музыки, /help — помощь"
    )

async def music(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Тестовая команда /music"""
    await update.message.reply_text("Команда /music сработала! Скоро тут генерация трека 🎶\n"
                                    "Пока просто эхо: " + (update.message.text or "пусто"))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Помощь: пиши тему песни, я придумаю текст и промпт для музыки!")

async def echo_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Эхо на всё, что не поймали команды (для теста)"""
    text = update.message.text
    if text:
        await update.message.reply_text(f"Эхо: {text}\n(Если это команда — добавь хендлер!)")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("music", music))
    application.add_handler(CommandHandler("help", help_command)) 

    application.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, echo_all))

    port = int(os.getenv("PORT", "8080"))
    full_webhook_url = f"{WEBHOOK_URL.rstrip('/')}{WEBHOOK_PATH}"

    logger.info(f"Starting webhook on {full_webhook_url}")

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=WEBHOOK_PATH,
        webhook_url=full_webhook_url,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
