from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Card, Column
from app.schemas.schemas import CardCreate, CardOut, CardUpdate
from app.websockets.manager import manager


class CardService:
    @staticmethod
    async def create(
        data: CardCreate,
        db: AsyncSession,
        board_id: int,
    ) -> CardOut:
        col = await db.get(Column, data.column_id)

        if not col or col.board_id != board_id:
            raise HTTPException(
                status_code=404,
                detail="Column not found",
            )

        card = Card(**data.model_dump())

        db.add(card)
        await db.flush()

        out = CardOut.model_validate(card)

        await manager.broadcast(
            board_id,
            {
                "type": "card_created",
                "card": out.model_dump(mode="json"),
            },
        )

        return out

    @staticmethod
    async def move(
        card_id: int,
        data: CardUpdate,
        db: AsyncSession,
        board_id: int,
    ) -> CardOut:
        card = await db.get(Card, card_id)

        if not card:
            raise HTTPException(
                status_code=404,
                detail="Card not found",
            )

        old_col_id = card.column_id

        if data.column_id is not None:
            target_col = await db.get(
                Column,
                data.column_id,
            )

            if not target_col or target_col.board_id != board_id:
                raise HTTPException(
                    status_code=404,
                    detail="Column not found",
                )

        for field, value in data.model_dump(
            exclude_none=True
        ).items():
            setattr(card, field, value)

        if (
            data.column_id is not None
            and data.position is not None
        ):
            result = await db.execute(
                select(Card)
                .where(
                    Card.column_id == data.column_id,
                    Card.id != card_id,
                )
                .order_by(Card.position)
            )

            siblings = result.scalars().all()

            for index, sibling in enumerate(siblings):
                sibling.position = (
                    index
                    if index < data.position
                    else index + 1
                )

        await db.flush()

        out = CardOut.model_validate(card)

        await manager.broadcast(
            board_id,
            {
                "type": "card_moved",
                "card_id": card_id,
                "old_column_id": old_col_id,
                "new_column_id": card.column_id,
                "position": card.position,
            },
        )

        return out

    @staticmethod
    async def delete(
        card_id: int,
        db: AsyncSession,
        board_id: int,
    ) -> None:
        card = await db.get(Card, card_id)

        if not card:
            raise HTTPException(
                status_code=404,
                detail="Card not found",
            )

        await db.delete(card)

        await manager.broadcast(
            board_id,
            {
                "type": "card_deleted",
                "card_id": card_id,
            },
        )
