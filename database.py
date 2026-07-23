import aiosqlite
import datetime

DB_NAME = 'bot_database.db'


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0,
            reg_date TEXT)''')

        await db.execute('''CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            stars_count INTEGER,
            price REAL,
            recipient TEXT,
            status TEXT,
            date TEXT)''')
        await db.commit()


async def add_user(user_id, username):
    async with aiosqlite.connect(DB_NAME) as db:
        reg_date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        await db.execute("INSERT OR IGNORE INTO users (user_id, username, balance, reg_date) VALUES (?, ?, ?, ?)",
                         (user_id, username, 0.0, reg_date))
        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()


async def update_balance(user_id, amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()




async def add_order(user_id, stars_count, price, recipient):
    """Записываем успешную покупку звезд"""
    async with aiosqlite.connect(DB_NAME) as db:
        date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        await db.execute(
            "INSERT INTO orders (user_id, stars_count, price, recipient, status, date) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, stars_count, price, recipient, "success", date)
        )
        await db.commit()


async def get_user_stats(user_id):
    """Получаем статистику покупок пользователя"""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
      
        sql = "SELECT COUNT(*) as total_orders, SUM(stars_count) as total_stars, SUM(price) as total_spent FROM orders WHERE user_id = ?"
        async with db.execute(sql, (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_all_users_count():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            res = await cursor.fetchone()
            return res[0]

async def get_total_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT SUM(price) as revenue, SUM(stars_count) as stars FROM orders") as cursor:
            return await cursor.fetchone()

async def get_all_user_ids():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def set_user_balance(user_id, amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET balance = ? WHERE user_id = ?", (amount, user_id))
        await db.commit()
