from sqlalchemy import Integer, BigInteger, Text, String, DateTime, ForeignKey, Enum, Boolean, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column, Session, joinedload
from sqlalchemy.sql import func

from aiogram.utils.link import create_tg_link
from aiogram import html

import typing as tp

from datetime import datetime

from ..environment import Base
from ..caching_query import FromCache


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"))

    text: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    provided_answer: Mapped[str] = mapped_column(Text, nullable=False)

    correctness: Mapped[float] = mapped_column(Float, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now())
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
