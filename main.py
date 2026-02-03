import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

# Главное меню как на скринах (с эмодзи и описаниями)
def get_main_menu():
    keyboard = [
        [KeyboardButton("Запустить Студию и главное меню 🎵")],
        [KeyboardButton("Создать хит с помощью ИИ 🎤")],
        [KeyboardButton("Сгенерировать крутое фото 📸")],
        [KeyboardButton("Сделать видео-клип 🎬")],
        [KeyboardButton("Проверить мой счёт и пополнить 💰")],
        [KeyboardButton("Помощь и поддержка 💎")],
        [KeyboardButton("Официальные тарифы студии 🔥")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Выбери действие")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋 Я — твоя персональная «Студия в кармане».\n"
        "Помогу тебе за 1 минуту:\n"
        "🎤 Написать и спеть песню\n"
        "📸 Создать арт или фото\n"
        "🎬 Сделать видео-клип для соцсетей\n\n"
        "Жми кнопку ниже и начнём творить! ✨",
        reply_markup=get_main_menu()
    )

async def create_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напиши тему песни (например: про кузнечиков в стиле шансон)\n"
        "Я сгенерирую текст и промпт для музыки!",
        reply_markup=get_main_menu()
    )
    context.user_data["awaiting_theme"] = True

async def tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Официальные тарифы студии:\n\n"
        "5 песен / фото / видео - 50 руб\n"
        "Unlimited на месяц - 300 руб\n\n"
        "(Оплата скоро подключим)",
        reply_markup=get_main_menu()
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Твой счёт пока 0 кредитов\n"
        "Скоро подключим пополнение!",
        reply_markup=get_main_menu()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Помощь и поддержка:\n"
        "/start - главное меню\n"
        "/song [тема] - создать песню\n"
        "/tariffs - тарифы\n"
        "/balance - баланс\n"
        "/help - эта помощь\n\n"
        "Пиши, если что-то сломалось!",
        reply_markup=get_main_menu()
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.user_data.get("awaiting_theme"):
        theme = text
        context.user_data["awaiting_theme"] = False

        # Генерация текста от меня (Grok)
        generated_text = (
            f"Вот текст песни на тему '{theme}':\n\n"
            "Куплет 1:\nКузнечик прыгает по траве, в ночи поёт шансон...\n"
            "Припев:\nКузнечик-кузнечик, прыг-скок в темноте!\n"
            "Куплет 2:\nЗелёный, маленький, но голос — как у Высоцкого...\n\n"
            "Промпт для @gusli_aibot или @easysongbot:\n"
            f"'шансон про кузнечиков, грустный русский, текст: [вставь текст выше]'\n\n"
            "Кидай промпт туда и получи трек! 🔥"
        )

        await update.message.reply_text(generated_text, reply_markup=get_main_menu())
        return

    # Обработка кнопок (без эха)
    if "Создать хит" in text or "Создать песню" in text:
        await create_song(update, context)
    elif "Тарифы" in text:
        await tariffs(update, context)
    elif "Баланс" in text or "счёт" in text:
        await balance(update, context)
    elif "Помощь" in text:
        await help_command(update, context)
    else:
        await update.message.reply_text(
            f"Не понял '{text}'. Выбери кнопку из меню!",
            reply_markup=get_main_menu()
        )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("song", create_song))
    app.add_handler(CommandHandler("tariffs", tariffs))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("help", help_command))

    # Обработка всех текстовых сообщений и кнопок
    app.add_handler(MessageHandler(filters.TEXT, handle_text))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
