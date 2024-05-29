from aiohttp import web
from app.models import db

async def init_db(app: web.Application):
    await db.set_bind(app['config'].DATABASE_URI)
