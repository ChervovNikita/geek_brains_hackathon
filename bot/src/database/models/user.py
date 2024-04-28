from sqlalchemy import Integer, BigInteger, Text, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column, Session, joinedload
from sqlalchemy.sql import func

from aiogram.utils.link import create_tg_link
from aiogram import html

import typing as tp

from datetime import datetime

from .quiz import Quiz
from ..environment import Base
from ..caching_query import FromCache


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    username: Mapped[str] = mapped_column(String(32), nullable=True)

    register_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now())

    quizzes: Mapped[list["Quiz"]] = relationship("Quiz")

    @staticmethod
    def create(
            session: Session,
            user_id: int,
            first_name: str,
            last_name: tp.Optional[str],
            username: tp.Optional[str]
    ) -> "User":
        user = User(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        session.add(user)
        session.commit()
        return user

    def update(
            self,
            session: Session,
            first_name: str,
            last_name: str | None,
            username: str | None
    ) -> None:
        updated = False
        for key, value in zip(
                ['first_name', 'last_name', 'username'],
                [first_name, last_name, username]
        ):
            if getattr(self, key) != value:
                setattr(self, key, value)
                updated = True
        if updated:
            session.commit()

    @staticmethod
    def get(
            session: Session,
            user_id: int
    ) -> tp.Optional["User"]:
        return session.query(User).options(FromCache(), joinedload(User.quizzes)).filter_by(id=user_id).first()

    @property
    def full_name(self) -> str:
        return " ".join([part for part in [self.first_name, self.last_name] if part])

    @property
    def link(self) -> str:
        return create_tg_link("user", id=self.id)

    @property
    def mention(self) -> str:
        return f"@{self.username}" if self.username else html.link(value=self.full_name, link=self.link)
