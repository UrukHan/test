from app.models import db, User, Transaction
from app.config import Config
import asyncio

async def create_tables():
    await db.set_bind(Config.DATABASE_URI)
    await db.gino.drop_all()
    print("Создание таблиц...")
    await db.gino.create_all()
    print("Таблицы успешно созданы")

loop = asyncio.get_event_loop()
loop.run_until_complete(create_tables())
