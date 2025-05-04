from datetime import date
import random
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from telegram import Update
from telegram.ext import ContextTypes
from models import Event, Category, CountryEvent, CategoryEvent
from database import SessionLocal


async def send_events(update: Update, events):
    if not events:
        await update.message.reply_text("События не найдены.")
        return

    for event in events:
        categories = ", ".join(c.category for c in event.categories) if event.categories else "нет категорий"
        countries = ", ".join(event.countries) if event.countries else "нет стран"

        message = (
            f"📅 <b>{event.date.strftime('%d.%m.%Y')}</b>\n"
            f"📌 <b>Событие:</b> {event.event}\n"
            f"🌍 <b>Страны:</b> {countries}\n"
            f"🏷 <b>Категории:</b> {categories}\n"
        )
        await update.message.reply_text(message, parse_mode='HTML')


async def handle_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    async with SessionLocal() as session:
        try:
            if len(args) == 1 and args[0].isdigit():
                year = int(args[0])
                start_date = date(year, 1, 1)
                end_date = date(year, 12, 31)
            elif len(args) == 3 and args[1] == "-":
                start, end = int(args[0]), int(args[2])
                start_date = date(start, 1, 1)
                end_date = date(end, 12, 31)
            else:
                raise ValueError
        except (ValueError, IndexError):
            await update.message.reply_text("Неверный формат. Используйте /year 1945 или /year 1941 - 1945.")
            return

        stmt = select(Event).options(
            selectinload(Event.category_links).selectinload(CategoryEvent.category),
            selectinload(Event.country_links)
        ).filter(Event.date.between(start_date, end_date))

        result = await session.execute(stmt)
        events = result.scalars().all()
        await send_events(update, events)


async def handle_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = date.today().strftime("%m-%d")
    async with SessionLocal() as session:
        stmt = select(Event).options(
            selectinload(Event.category_links).selectinload(CategoryEvent.category),
            selectinload(Event.country_links)
        ).filter(func.to_char(Event.date, 'MM-DD') == today)

        result = await session.execute(stmt)
        events = result.scalars().all()
        await send_events(update, events)


async def handle_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with SessionLocal() as session:
        stmt = select(Event).options(
            selectinload(Event.category_links).selectinload(CategoryEvent.category),
            selectinload(Event.country_links)
        )
        result = await session.execute(stmt)
        events = result.scalars().all()
        if events:
            event = random.choice(events)
            await send_events(update, [event])


async def handle_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country_name = " ".join(context.args)
    if not country_name:
        await update.message.reply_text("Укажите страну: /country Россия")
        return

    async with SessionLocal() as session:
        stmt = select(Event).join(Event.country_links).filter(
            CountryEvent.country.ilike(f"%{country_name}%")
        ).options(
            selectinload(Event.category_links).selectinload(CategoryEvent.category),
            selectinload(Event.country_links)
        )
        result = await session.execute(stmt)
        events = result.scalars().all()
        await send_events(update, events)


async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category_name = " ".join(context.args)
    if not category_name:
        await update.message.reply_text("Укажите категорию: /category Политика")
        return

    async with SessionLocal() as session:
        stmt = select(Event).join(Event.category_links).join(Category).filter(
            Category.category.ilike(f"%{category_name}%")
        ).options(
            selectinload(Event.category_links).selectinload(CategoryEvent.category),
            selectinload(Event.country_links)
        )
        result = await session.execute(stmt)
        events = result.scalars().all()
        await send_events(update, events)