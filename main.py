import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
import database as db

# Импортируем все хендлеры
from handlers import start, payment, stars, admin

logging.basicConfig(level=logging.INFO)

async def main():
    await db.init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # ПОДКЛЮЧАЙТЕ КАЖДЫЙ РОУТЕР ТОЛЬКО ОДИН РАЗ!
    # Если вы добавили админку, убедитесь, что список выглядит так:
    dp.include_routers(
        admin.router,
        start.router,
        payment.router,
        stars.router
    )

    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())