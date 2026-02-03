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

# Логируем всё подробно
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG  # DEBUG для максимума инфы
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set!")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL not set!")

WEBHOOK_PATH = "/webhook"

# Обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug("Получена команда /start")
    user = update.effective_user
    await update.message.reply_text(
        f"Дарова, {user.first_name}! Я Студия в кармане 🎤✨\n"
        "Кидай тему песни — скоро сделаем трек!\n"
        "Команды: /help, /music, /tariffs, /balance, /photo, /video"
    )

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug("Получена команда /help")
    await update.message.reply_text("Пока бот в тесте. Скоро: генерация песен, текст + музыка!")

# /music
async def music(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug("Получена команда /music")
    await update.message.reply_text("Генерация музыки пока в разработке 🎶\nПришли тему — подготовлю промпт!")

# /tariffs
async def tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug("Получена команда /tariffs")
    await update.message.reply_text("Тарифы:\n1 песня бесплатно\n5 песен — 50 руб\nUnlimited — 300 руб/мес (скоро)")

# /balance
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug("Получена команда /balance")
    await update.message.reply_text("Баланс: 0 руб (пока тестовый режим)")

# /photo, /video — заглушки
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug("Получена команда /photo")
    await update.message.reply_text("Генерация фото пока не готова 📸")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug("Получена команда /video")
    await update.message.reply_text("Генерация видео в планах 🎥")

# Ловит ВСЁ остальное (текст, любые команды, фото и т.д.)
async def catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug(f"Поймано сообщение: {update.message.text or 'не текст'}")
    text = update.message.text or "не текст"
    await update.message.reply_text(f"Эхо: {text}\n(Если это команда — она должна была сработать выше)")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Регистрируем все команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("music", music))
    application.add_handler(CommandHandler("tariffs", tariffs))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("photo", photo))
    application.add_handler(CommandHandler("video", video))

    # Ловим всё остальное (текст + команды, если не пойманы выше)
    application.add_handler(MessageHandler(filters.ALL, catch_all))

    port = int(os.getenv("PORT", "8080"))
    full_webhook_url = f"{WEBHOOK_URL.rstrip('/')}{WEBHOOK_PATH}"

    logger.info(f"Запуск webhook на {full_webhook_url}")

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=WEBHOOK_PATH,
        webhook_url=full_webhook_url,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES  # Разрешаем все типы обновлений
    )

if __name__ == "__main__":
    main()
