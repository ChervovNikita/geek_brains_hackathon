from sqlalchemy.orm import Session
from aiogram import types

from .models import User


def get_user(
        session: Session,
        telegram_user: types.User,
        create: bool = False
) -> User | None:
    user = User.get(session, telegram_user.id)

    if user is None:
        if not create:
            return None

        user = User.create(
            session,
            telegram_user.id,
            telegram_user.first_name,
            telegram_user.last_name,
            telegram_user.username
        )
    else:
        user.update(
            session,
            telegram_user.first_name,
            telegram_user.last_name,
            telegram_user.username
        )

    return user
