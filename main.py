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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug("Получена команда /start")
    user = update.effective_user
    await update.message.reply_text(f"Дарова, {user.first_name}! Я работаю на polling теперь 🔥")

async def catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug(f"Поймано сообщение: {update.message.text}")
    await update.message.reply_text(f"Эхо: {update.message.text}")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, catch_all))

    logger.info("Запуск polling...")

    application.run_polling(
        drop_pending_updates=True,
        poll_interval=0.5,
        timeout=10,
        bootstrap_retries=-1,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
