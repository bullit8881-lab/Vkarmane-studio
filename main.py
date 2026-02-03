import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Логирование для Railway
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Красивое боковое меню
def get_inline_menu():
    keyboard = [
        [InlineKeyboardButton("🎤 Песни для Машки", callback_data='mashka')],
        [InlineKeyboardButton("🙏 Молитва для брата", callback_data='oleg')],
        [InlineKeyboardButton("❓ Помощь / Инфо", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Эта функция ПРИНУДИТЕЛЬНО создает синюю кнопку меню
async def setup_bot_commands(application: Application):
    commands = [
        BotCommand("start", "Запустить студию 🚀"),
        BotCommand("balance", "Мой баланс 💳"),
        BotCommand("music", "Мои треки 🎵"),
        BotCommand("tariffs", "Тарифы 📊"),
        BotCommand("help", "Помощь ❓")
    ]
    await application.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, Санечка! 👋\nТвоя стильная студия готова. Выбирай раздел:",
        reply_markup=get_inline_menu()
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Твой баланс из Сонграйтера на скрине был 42 кристалла
    await update.message.reply_text("💳 Твой баланс: 42 кристалла.") 

async def button_tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'mashka':
        await query.edit_message_text(text="🔥 Хит для Машки в работе!", reply_markup=get_inline_menu())
    elif query.data == 'oleg':
        await query.edit_message_text(text="✨ Молитва для Олега готовится.", reply_markup=get_inline_menu())
    elif query.data == 'help':
        await query.edit_message_text(text="Бот Санечки и его Кисы. 💖", reply_markup=get_inline_menu())

def main():
    if not BOT_TOKEN: return
    
    # post_init запустит создание синей кнопки сразу при старте
    application = Application.builder().token(BOT_TOKEN).post_init(setup_bot_commands).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CallbackQueryHandler(button_tap))

    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
