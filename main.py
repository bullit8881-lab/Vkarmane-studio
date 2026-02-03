import logging
import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    PreCheckoutQueryHandler,
    CallbackQueryHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токены из переменных Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")  # из BotFather (YooMoney или Stars)

# Файл для хранения баланса пользователей
BALANCE_FILE = "user_balances.json"

# Цена одной песни в кредитах
SONG_COST = 1

# Загружаем / сохраняем балансы
def load_balances():
    try:
        with open(BALANCE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_balances(balances):
    with open(BALANCE_FILE, "w") as f:
        json.dump(balances, f, indent=4)

user_balances = load_balances()

# Главная клавиатура
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🎤 Создать песню")],
        [KeyboardButton("💰 Тарифы")],
        [KeyboardButton("💳 Баланс")],
        [KeyboardButton("❓ Помощь")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Приветствие /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_balances:
        user_balances[user_id] = 3  # стартовые 3 песни бесплатно
        save_balances(user_balances)

    text = (
        "Дарова, братан! 👋\n"
        "Это твоя личная студия в кармане 🔥\n"
        "Я — Grok, и я здесь, чтобы писать тебе треки, как дома.\n"
        "Кидай любую тему — я пойму и зарифмую.\n\n"
        "Жми кнопку ниже или пиши /song [тема]"
    )
    await update.message.reply_text(text, reply_markup=get_main_keyboard())

# Команда /song или кнопка "Создать песню"
async def create_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    balance = user_balances.get(user_id, 0)

    if balance < SONG_COST:
        keyboard = [[InlineKeyboardButton("Пополнить баланс 💳", callback_data="buy")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Брат, кредиты кончились (у тебя {balance}).\n"
            "Жми «Тарифы» или пополни баланс!",
            reply_markup=reply_markup
        )
        return

    if context.args:
        theme = " ".join(context.args)
        await generate_song(update, context, theme)
    else:
        await update.message.reply_text(
            "Кидай тему песни, братан!\n"
            "Примеры:\n"
            "про погоду в Питере\n"
            "грустный рэп про завод\n"
            "весёлый шансон про кузнечиков",
            reply_markup=get_main_keyboard()
        )
        context.user_data["awaiting_song_theme"] = True

# Обработка обычного текста (тема песни или другие сообщения)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()

    if context.user_data.get("awaiting_song_theme"):
        context.user_data["awaiting_song_theme"] = False
        await generate_song(update, context, text)
        return

    # Если не тема — просто эхо или подсказка
    await update.message.reply_text(
        f"Брат, я понял: «{text}»\n"
        "Если это тема песни — пиши /song [тема]\n"
        "Или жми кнопку «Создать песню» 🎤",
        reply_markup=get_main_keyboard()
    )

# Генерация песни (от Grok)
async def generate_song(update: Update, context: ContextTypes.DEFAULT_TYPE, theme: str):
    user_id = str(update.effective_user.id)
    balance = user_balances.get(user_id, 0)

    if balance < SONG_COST:
        await update.message.reply_text("Кредиты кончились! Пополни баланс.")
        return

    msg = await update.message.reply_text("Ща замутим трек... 🔥 Подожди 5–15 сек...")

    try:
        # Здесь я (Grok) генерирую текст песни
        prompt = (
            f"Напиши крутой текст песни на тему: '{theme}'.\n"
            "Сделай 2 куплета + припев + бридж.\n"
            "Стиль — любой, но цепляющий, можно с матом, если в тему.\n"
            "В конце добавь готовый промпт для @gusli_aibot или Suno/Udio."
        )

        # Симуляция ответа Grok (в реальности ты получаешь мой ответ через API или напрямую)
        # Для теста оставляем пример, но в продакшене здесь будет реальный вызов
        song_text = (
            f"Тема: {theme}\n\n"
            "Куплет 1:\n"
            "Дождь барабанит по крыше завода,\n"
            "Смена кончилась, но душа всё равно мокрая...\n\n"
            "Припев:\n"
            "Погода плачет, как я по тебе,\n"
            "Но я всё равно иду вперёд, не сдамся, нет!\n\n"
            "Куплет 2:\n"
            "Кузнечик в луже тонет, но поёт,\n"
            "Как будто завтра солнце снова взойдёт...\n\n"
            "Промпт для @gusli_aibot:\n"
            f"'грустный русский шансон/рэп про {theme}, текст: [вставь текст выше], голос низкий, бит тяжёлый'"
        )

        user_balances[user_id] = balance - SONG_COST
        save_balances(user_balances)

        await msg.edit_text(
            f"Готово, братан! 🔥\n\n{song_text}\n\n"
            f"Осталось кредитов: {user_balances[user_id]}\n"
            "Кидай промпт в @gusli_aibot и получи трек!",
            reply_markup=get_main_keyboard()
        )

    except Exception as e:
        await msg.edit_text(f"Бля, что-то сломалось: {str(e)}\nПопробуй ещё раз.")

# Тарифы
async def tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("5 кредитов — 50 ₽", callback_data="buy_5")],
        [InlineKeyboardButton("20 кредитов — 150 ₽", callback_data="buy_20")],
        [InlineKeyboardButton("Unlimited на месяц — 499 ₽", callback_data="buy_unlim")],
    ])
    await update.message.reply_text(
        "Тарифы студии:\n\n"
        "1 песня = 1 кредит\n\n"
        "Выбери пакет:",
        reply_markup=keyboard
    )

# Баланс
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    bal = user_balances.get(user_id, 0)
    await update.message.reply_text(
        f"Твой баланс: {bal} кредитов\n"
        "1 песня = 1 кредит",
        reply_markup=get_main_menu()
    )

# Обработка кнопок оплаты
async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    prices = {
        "buy_5": [LabeledPrice("5 кредитов", 5000)],
        "buy_20": [LabeledPrice("20 кредитов", 15000)],
        "buy_unlim": [LabeledPrice("Unlimited месяц", 49900)],
    }

    payload = query.data
    price = prices.get(payload, prices["buy_5"])

    await context.bot.send_invoice(
        chat_id=query.from_user.id,
        title="Пополнение студии",
        description="Кредиты для генерации песен",
        payload=payload,
        provider_token=PAYMENT_TOKEN,
        currency="RUB",
        prices=price,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
    )

# Предпроверка оплаты
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)

# Успешная оплата
async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    payload = update.message.successful_payment.invoice_payload

    credits = {"buy_5": 5, "buy_20": 20, "buy_unlim": 9999}.get(payload, 0)

    user_balances[user_id] = user_balances.get(user_id, 0) + credits
    save_balances(user_balances)

    await update.message.reply_text(
        f"Спасибо, брат! 🔥\n"
        f"Пополнено {credits} кредитов.\n"
        f"Текущий баланс: {user_balances[user_id]}\n\n"
        "Готов творить? Жми «Создать песню» 🎤",
        reply_markup=get_main_menu()
    )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("song", create_song))
    app.add_handler(CommandHandler("tariffs", tariffs))
    app.add_handler(CommandHandler("balance", balance))

    app.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy_"))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
