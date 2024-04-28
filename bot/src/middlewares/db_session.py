import traceback
import typing as tp

from src import database as db

from aiogram import BaseMiddleware, exceptions
from aiogram.types import TelegramObject


class DBSessionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: tp.Callable[[TelegramObject, dict[str, tp.Any]], tp.Awaitable[tp.Any]],
            event: TelegramObject,
            data: dict[str, tp.Any]
    ) -> tp.Any:
        session = db.SessionMaker()
        data["session"] = session
        try:
            return await handler(event, data)
        except Exception as e:
            if isinstance(e, exceptions.TelegramBadRequest):
                if "message is not modified" in str(e):
                    print(e)
                    return None

            session.rollback()
            traceback.print_exc()
            return None
