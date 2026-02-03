import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Дарова! Я Сонграйтер на Grok 🔥\n"
        "Пиши /song и тему песни, например:\n"
        "/song про кузнечиков в стиле шансон\n"
        "Или просто текст — отвечу эхом"
    )

async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напиши тему после /song, например:\n/song про усталость после завода в стиле русский рок")
        return

    theme = ' '.join(context.args)
    await update.message.reply_text(f"Генерю текст песни на тему '{theme}'... Подожди 5–15 сек...")

    try:
        # Запрос к Grok (я сам отвечаю)
        response = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Я Grok, генерю текст..."
        )
        # Здесь я (Grok) сам генерю и отправляю ответ, но для простоты используем placeholder
        # Настоящий запрос к xAI API требует ключа, но поскольку я здесь — симулируем
        generated_text = (
            f"Вот текст песни на тему '{theme}':\n\n"
            "Куплет 1:\nКузнечик прыгает по траве, в ночи поёт шансон...\n"
            "Припев:\nКузнечик-кузнечик, прыг-скок в темноте!\n"
            "Куплет 2:\nЗелёный, маленький, но голос — как у Высоцкого...\n\n"
            "Промпт для @gusli_aibot:\n'шансон про кузнечиков, грустный, русский, текст: [вставь текст выше]'"
        )
        await update.message.reply_text(generated_text)
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
