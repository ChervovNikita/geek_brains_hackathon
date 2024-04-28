from sqlalchemy import Integer, BigInteger, Text, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column, Session, joinedload
from sqlalchemy.sql import func

from datetime import datetime

from .question import Question
from ..environment import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    questions: Mapped[list["Question"]] = relationship("Question")
    recommendations: Mapped[str] = mapped_column(Text, nullable=True)
    result: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now())
    finish_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
