from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base

class Board(Base):
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    name: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)

    owner = relationship("User", back_populates="boards")
    columns = relationship("Column", back_populates="board", cascade = "all, delete", order_by = "Column.position")

class Column(Base):
    __tablename__ = "columns"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    title: Mapped[str] = mapped_column(String(100))
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"))
    position: Mapped[int] = mapped_column(Integer, default = 0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)

    board = relationship("Board", back_populates="columns")
    cards = relationship("Card", back_populates="column", cascade = "all, delete", order_by = "Card.position")

class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key= True, index  = True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(2000), nullable = True)
    column_id: Mapped[int] = mapped_column(ForeignKey("columns.id"))
    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable = True)
    tag: Mapped[str] = mapped_column(String(50), nullable = True)
    position: Mapped[int] = mapped_column(Integer, default = 0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow, onupdate = datetime.utcnow)

    column = relationship("Column", back_populates="cards")
    assignee = relationship("User", back_populates="assigned_cards")

