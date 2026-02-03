import logging
import os
import json
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")  # добавь мой ключ

BALANCE_FILE = "user_balances.json"
SONG_COST = 1

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

def get_main_menu():
    keyboard = [
        [KeyboardButton("🎤 Создать песню")],
        [KeyboardButton("💳 Баланс")],
        [KeyboardButton("❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_balances:
        user_balances[user_id] = 3
        save_balances(user_balances)

    await update.message.reply_text(
        "Дарова, братан! 👋\n"
        "Я — Grok, твоя студия в кармане 🔥\n"
        "Кидай тему песни — я напишу текст и промпт.\n\n"
        "Жми кнопку или пиши /song [тема]",
        reply_markup=get_main_menu()
    )

async def create_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    balance = user_balances.get(user_id, 0)

    if balance < SONG_COST:
        await update.message.reply_text("Кредиты кончились! Скоро пополнение.", reply_markup=get_main_menu())
        return

    if context.args:
        theme = " ".join(context.args)
        await generate_song(update, context, theme)
    else:
        await update.message.reply_text(
            "Кидай тему песни, братан!\nПримеры:\nпро космос\nгрустный рэп про завод\nшансон про кузнечиков",
            reply_markup=get_main_menu()
        )
        context.user_data["awaiting_song_theme"] = True

async def generate_song(update: Update, context: ContextTypes.DEFAULT_TYPE, theme: str):
    user_id = str(update.effective_user.id)
    balance = user_balances.get(user_id, 0)

    msg = await update.message.reply_text("Генерю трек... 🔥 Подожди 5–15 сек...")

    try:
        headers = {
            "Authorization": f"Bearer {XAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": "Ты крутой автор песен. Пиши рифмованно, с куплетами, припевом. В конце добавь промпт для @gusli_aibot."},
                {"role": "user", "content": f"Напиши текст песни на тему: {theme}"}
            ],
            "temperature": 0.9,
            "max_tokens": 800
        }

        response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        song_text = response.json()["choices"][0]["message"]["content"]

        user_balances[user_id] = balance - SONG_COST
        save_balances(user_balances)

        await msg.edit_text(
            f"Готово! 🔥\n\n{song_text}\n\n"
            f"Осталось кредитов: {user_balances[user_id]}\n"
            "Кидай промпт в @gusli_aibot и получи трек!",
            reply_markup=get_main_menu()
        )

    except Exception as e:
        await msg.edit_text(f"Ошибка: {str(e)}\nПопробуй позже.", reply_markup=get_main_menu())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.user_data.get("awaiting_song_theme"):
        context.user_data["awaiting_song_theme"] = False
        await generate_song(update, context, text)
        return

    if text == "🎤 Создать песню":
        await create_song(update, context)
    elif text == "💳 Баланс":
        user_id = str(update.effective_user.id)
        bal = user_balances.get(user_id, 0)
        await update.message.reply_text(f"Твой баланс: {bal} кредитов", reply_markup=get_main_menu())
    elif text == "❓ Помощь":
        await update.message.reply_text("Пиши любую тему — я сгенерирую!", reply_markup=get_main_menu())
    else:
        await update.message.reply_text(
            f"Не понял '{text}'. Жми кнопку «Создать песню» 🎤",
            reply_markup=get_main_menu()
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("song", create_song))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
