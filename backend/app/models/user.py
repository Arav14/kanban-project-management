from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    boards = relationship(
        "Board",
        back_populates="owner",
        cascade="all, delete",
    )

    assigned_cards = relationship(
        "Card",
        back_populates="assignee",
    )
