import asyncio
import json
import logging

from redis.asyncio.client import Redis

from aiogram import Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.fsm.storage.redis import RedisStorage

from src import handlers, configs
from src.middlewares import (
    IgnoreNotUserUpdates,
    DBUserMiddleware,
    DBSessionMiddleware,
)
from src.bot import bot


async def on_startup():
    logging.info('Bot is launched')


async def on_stop():
    logging.info('Bot stopped')


async def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s | %(levelname)s] %(module)s::%(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Initialize storage
    storage = RedisStorage(
        Redis(
            host=configs.REDIS_HOST,
            port=configs.REDIS_PORT,
            db=2,  # fsm
            decode_responses=True
        ),
        json_dumps=lambda data: json.dumps(data, ensure_ascii=False)
    )

    # Initialize dispatcher
    dp = Dispatcher(storage=storage)
    dp.include_routers(
        # handlers.misc.router,
        handlers.menu.router,
        handlers.course.router,
        handlers.quiz.router,
    )

    if configs.DEBUG:  # skip updates
        await bot(DeleteWebhook(drop_pending_updates=True))

    dp.update.outer_middleware(DBSessionMiddleware())
    dp.update.outer_middleware(IgnoreNotUserUpdates())

    dp.message.outer_middleware(DBUserMiddleware())
    dp.callback_query.outer_middleware(DBUserMiddleware())

    dp.startup.register(on_startup)
    dp.shutdown.register(on_stop)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await dp.storage.close()


if __name__ == '__main__':
    asyncio.run(main())
