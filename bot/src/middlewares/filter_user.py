import typing as tp

from aiogram import BaseMiddleware
from aiogram.types import Update, TelegramObject


class IgnoreNotUserUpdates(BaseMiddleware):
    async def __call__(
            self,
            handler: tp.Callable[[TelegramObject, dict[str, tp.Any]], tp.Awaitable[tp.Any]],
            event: Update,
            data: dict[str, tp.Any]
    ) -> tp.Any:
        if event.event_type not in ["message", "callback_query"]:
            return
        # Message not from user:
        if event.event_type == "message" and not hasattr(event.message.from_user, "last_name"):
            return
        # CallbackQuery not from user (not possible in current telegram version):
        if event.event_type == "callback_query" and not hasattr(event.callback_query.from_user, "last_name"):
            return
        return await handler(event, data)
