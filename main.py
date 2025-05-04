# main.py
from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from handlers import (
    handle_year, handle_day, handle_random,
    handle_country, handle_category
)
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("События по году", callback_data="year")],
        [InlineKeyboardButton("Событие по дню", callback_data="day")],
        [InlineKeyboardButton("Случайное событие", callback_data="random")],
        [InlineKeyboardButton("По стране", callback_data="country")],
        [InlineKeyboardButton("По категории", callback_data="category")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите тип запроса:", reply_markup=reply_markup)

async def handle_button(update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(f"Введите команду /{query.data} ...")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("year", handle_year))
    app.add_handler(CommandHandler("day", handle_day))
    app.add_handler(CommandHandler("random", handle_random))
    app.add_handler(CommandHandler("country", handle_country))
    app.add_handler(CommandHandler("category", handle_category))

    app.run_polling()

if __name__ == "__main__":
    main()