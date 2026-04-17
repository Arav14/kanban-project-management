from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    email: Mapped[str] = mapped_column(String(255), unique = True, index = True)
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)

    boards = relationship("Board", back_populates = "owner", cascade = "all, delete")
    assigned_cards = relationship("Card", back_populates="assignee")

