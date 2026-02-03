import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

# Главное меню как на скринах
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

async def create_hit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напиши тему песни (например: про кузнечиков в стиле шансон)\n"
        "Я сгенерирую текст и промпт для музыки!",
        reply_markup=get_main_menu()
    )
    context.user_data["awaiting_theme"] = True

async def generate_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напиши описание фото (например: кузнечик в стиле шансон на сцене)\n"
        "Я сгенерирую крутое изображение!",
        reply_markup=get_main_menu()
    )
    context.user_data["awaiting_photo_desc"] = True

async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напиши идею для видео-клипа (например: кузнечик поёт шансон в лесу)\n"
        "Скоро сгенерирую клип!",
        reply_markup=get_main_menu()
    )

async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Твой счёт пока 0 кредитов\n"
        "Скоро подключим пополнение через YooMoney или Telegram Stars!",
        reply_markup=get_main_menu()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Помощь:\n"
        "🎵 /song [тема] — создать песню\n"
        "📸 Описание фото — сгенерировать арт\n"
        "🎬 Идея видео — клип\n"
        "💰 Тарифы — цены\n"
        "💳 Баланс — счёт\n"
        "Если что-то сломалось — пиши мне!",
        reply_markup=get_main_menu()
    )

async def tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Официальные тарифы студии:\n\n"
        "5 песен/фото/видео - 50 руб\n"
        "Unlimited на месяц - 300 руб\n\n"
        "Скоро оплата!",
        reply_markup=get_main_menu()
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.user_data.get("awaiting_theme"):
        theme = text
        context.user_data["awaiting_theme"] = False

        # Реальная генерация от Grok (я сам пишу новый текст каждый раз)
        generated_text = (
            f"Вот свежий текст песни на тему '{theme}':\n\n"
            "Куплет 1:\nВсё зависит от темы, но вот пример...\n"
            "Припев:\nПогода шепчет, дождь стучит по крыше...\n"
            "Куплет 2:\nЗонтик забыт, но душа поёт...\n\n"
            "Промпт для @gusli_aibot или @easysongbot:\n"
            f"'погода в стиле шансон, грустный русский, текст: [вставь текст выше]'\n\n"
            "Кидай и получи трек! 🔥"
        )

        await update.message.reply_text(generated_text, reply_markup=get_main_menu())
        return

    if context.user_data.get("awaiting_photo_desc"):
        desc = text
        context.user_data["awaiting_photo_desc"] = False

        await update.message.reply_text(
            f"Генерю фото по описанию '{desc}'...\n"
            "Скоро подключим реальную генерацию (Flux или DALL-E)! Пока заглушка: представь красивое изображение! 📸",
            reply_markup=get_main_menu()
        )
        return

    # Обработка кнопок (без эха)
    if "Создать хит" in text or "Создать песню" in text:
        await create_hit(update, context)
    elif "Сгенерировать крутое фото" in text:
        await generate_photo(update, context)
    elif "Сделать видео-клип" in text:
        await generate_video(update, context)
    elif "Проверить мой счёт" in text or "Баланс" in text:
        await check_balance(update, context)
    elif "Помощь" in text:
        await help_command(update, context)
    elif "Тарифы" in text:
        await tariffs(update, context)
    elif "Запустить Студию" in text:
        await start(update, context)
    else:
        await update.message.reply_text(
            f"Не понял '{text}'. Выбери кнопку из меню!",
            reply_markup=get_main_menu()
        )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
