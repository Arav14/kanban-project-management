from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.board import Board, Card, Column
from app.models.user import User
from app.schemas.schemas import (
    BoardCreate,
    BoardOut,
    CardCreate,
    CardOut,
    CardUpdate,
    ColumnCreate,
    ColumnOut,
    ColumnUpdate,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.services.auth_service import AuthService
from app.services.card_service import CardService
from app.websockets.manager import manager

router = APIRouter()


@router.post("/auth/register", response_model=TokenResponse)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await AuthService.register(data, db)


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await AuthService.login(data, db)


@router.get("/auth/me", response_model=UserOut)
async def me(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


@router.post("/boards", response_model=BoardOut)
async def create_board(
    data: BoardCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Board:
    board = Board(
        name=data.name,
        owner_id=user.id,
    )

    db.add(board)
    await db.flush()

    for position, title in enumerate(
        ("Backlog", "To Do", "In Progress", "In Review", "Done")
    ):
        db.add(
            Column(
                title=title,
                board_id=board.id,
                position=position,
            )
        )

    return board


@router.get("/boards", response_model=list[BoardOut])
async def list_boards(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Board]:
    result = await db.execute(
        select(Board).where(Board.owner_id == user.id)
    )

    return list(result.scalars().all())


@router.get("/boards/{board_id}")
async def get_board(
    board_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    board = await db.get(Board, board_id)

    if not board or board.owner_id != user.id:
        raise HTTPException(
            status_code=404,
            detail="Board not found",
        )

    result = await db.execute(
        select(Column)
        .where(Column.board_id == board_id)
        .order_by(Column.position)
    )

    columns = result.scalars().all()

    board_data = {
        "id": board_id,
        "name": board.name,
        "columns": [],
    }

    for col in columns:
        result = await db.execute(
            select(Card)
            .where(Card.column_id == col.id)
            .order_by(Card.position)
        )

        cards = result.scalars().all()

        board_data["columns"].append(
            {
                "id": col.id,
                "title": col.title,
                "position": col.position,
                "cards": [
                    CardOut.model_validate(card).model_dump(
                        mode="json"
                    )
                    for card in cards
                ],
            }
        )

    return board_data


@router.post(
    "/boards/{board_id}/columns",
    response_model=ColumnOut,
)
async def create_column(
    board_id: int,
    data: ColumnCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Column:
    board = await db.get(Board, board_id)

    if not board or board.owner_id != user.id:
        raise HTTPException(
            status_code=404,
            detail="Board not found",
        )

    col = Column(
        **data.model_dump(),
        board_id=board_id,
    )

    db.add(col)
    await db.flush()

    return col


@router.patch(
    "/boards/{board_id}/columns/{col_id}",
    response_model=ColumnOut,
)
async def update_column(
    board_id: int,
    col_id: int,
    data: ColumnUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Column:
    board = await db.get(Board, board_id)

    if not board or board.owner_id != user.id:
        raise HTTPException(
            status_code=404,
            detail="Board not found",
        )

    col = await db.get(Column, col_id)

    if not col or col.board_id != board_id:
        raise HTTPException(
            status_code=404,
            detail="Column not found",
        )

    for field, value in data.model_dump(
        exclude_none=True
    ).items():
        setattr(col, field, value)

    return col


@router.post(
    "/boards/{board_id}/cards",
    response_model=CardOut,
)
async def create_card(
    board_id: int,
    data: CardCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CardOut:
    board = await db.get(Board, board_id)

    if not board or board.owner_id != user.id:
        raise HTTPException(
            status_code=404,
            detail="Board not found",
        )

    return await CardService.create(
        data,
        db,
        board_id,
    )


@router.patch(
    "/boards/{board_id}/cards/{card_id}",
    response_model=CardOut,
)
async def update_card(
    board_id: int,
    card_id: int,
    data: CardUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CardOut:
    board = await db.get(Board, board_id)

    if not board or board.owner_id != user.id:
        raise HTTPException(
            status_code=404,
            detail="Board not found",
        )

    return await CardService.move(
        card_id,
        data,
        db,
        board_id,
    )


@router.delete("/boards/{board_id}/cards/{card_id}")
async def delete_card(
    board_id: int,
    card_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    board = await db.get(Board, board_id)

    if not board or board.owner_id != user.id:
        raise HTTPException(
            status_code=404,
            detail="Board not found",
        )

    await CardService.delete(
        card_id,
        db,
        board_id,
    )

    return {"message": "Card deleted"}


@router.websocket("/ws/{board_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    board_id: int,
) -> None:
    await manager.connect(
        websocket,
        board_id,
    )

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(
            websocket,
            board_id,
        )
