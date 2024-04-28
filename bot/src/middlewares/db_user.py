import typing as tp

from src import database as db

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import (
    TelegramObject,
    CallbackQuery,
    Message
)


class DBUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: tp.Callable[[TelegramObject, dict[str, tp.Any]], tp.Awaitable[tp.Any]],
            event: TelegramObject,
            data: dict[str, tp.Any]
    ) -> tp.Any:
        if not isinstance(event, (CallbackQuery, Message)):
            return await handler(event, data)
        event_chat = event.chat if isinstance(event, Message) else event.message.chat
        if event_chat.type == ChatType.CHANNEL:
            return
        user = db.get_user(data['session'], event.from_user, create=event_chat.type == ChatType.PRIVATE)
        data['user'] = user
        if user is None:
            return  # user not registered
        return await handler(event, data)
