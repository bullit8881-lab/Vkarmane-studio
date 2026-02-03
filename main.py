import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

# Главное меню
def get_main_menu():
    keyboard = [
        [KeyboardButton("Создать песню 🎤")],
        [KeyboardButton("Тарифы 💰")],
        [KeyboardButton("Баланс 💳")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Дарова! Выбери кнопку ниже:",
        reply_markup=get_main_menu()
    )

async def create_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напиши тему песни (например: про кузнечиков в стиле шансон)",
        reply_markup=get_main_menu()  # возвращаем главное меню
    )
    context.user_data["awaiting_theme"] = True  # ждём тему

async def tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Тарифы:\n5 песен - 50 руб\nUnlimited на месяц - 300 руб\n\n(Оплата скоро подключим)",
        reply_markup=get_main_menu()
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Баланс пока 0 кредитов\nСкоро подключим оплату!",
        reply_markup=get_main_menu()
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if context.user_data.get("awaiting_theme"):
        theme = text
        context.user_data["awaiting_theme"] = False

        # Генерация от Grok (пока заглушка, но в стиле)
        generated_text = f"Вот текст песни на тему '{theme}':\n\n" \
                         f"Куплет 1:\nКузнечик прыгает по траве, в ночи поёт шансон...\n" \
                         f"Припев:\nКузнечик-кузнечик, прыг-скок в темноте!\n" \
                         f"Куплет 2:\nЗелёный, маленький, но голос — как у Высоцкого...\n\n" \
                         f"Промпт для @gusli_aibot или @easysongbot:\n" \
                         f"'шансон про кузнечиков, грустный русский, текст: [вставь текст выше]'\n\n" \
                         f"Кидай промпт туда и получи трек! 🔥"

        await update.message.reply_text(generated_text, reply_markup=get_main_menu())
        return

    # Обработка кнопок
    if text == "Создать песню 🎤":
        await create_song(update, context)
    elif text == "Тарифы 💰":
        await tariffs(update, context)
    elif text == "Баланс 💳":
        await balance(update, context)
    else:
        await update.message.reply_text(f"Не понял '{text}'. Выбери кнопку из меню!", reply_markup=get_main_menu())

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
