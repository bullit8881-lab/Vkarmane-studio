import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_inline_menu():
    keyboard = [
        [InlineKeyboardButton("🎤 Песни для Машки", callback_data='mashka')],
        [InlineKeyboardButton("🙏 Молитва для брата", callback_data='oleg')],
        [InlineKeyboardButton("❓ Помощь / Инфо", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, Санечка! 👋\nТвоя стильная студия готова. Выбирай раздел:",
        reply_markup=get_inline_menu()
    )

async def button_tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'mashka':
        await query.edit_message_text(text="🔥 Готовим хит 'Королева Весны'!", reply_markup=get_inline_menu())
    elif query.data == 'oleg':
        await query.edit_message_text(text="✨ Песня 'Щит и Стена' для Олега.", reply_markup=get_inline_menu())
    elif query.data == 'help':
        await query.edit_message_text(text="Бот Санечки и его Кисы. 💖", reply_markup=get_inline_menu())

# Функция, которая настраивает ту самую СИНЮЮ кнопку
async def post_init(application: Application):
    commands = [
        BotCommand("start", "Запустить студию"),
        BotCommand("help", "Помощь"),
        BotCommand("balance", "Проверить баланс"),
        BotCommand("tariffs", "Тарифы"),
        BotCommand("music", "Моя музыка")
    ]
    await application.bot.set_my_commands(commands)

def main():
    if not BOT_TOKEN:
        return
    
    # Добавляем post_init для создания синей кнопки
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_tap))

    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
