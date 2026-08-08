from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class BoardCreate(BaseModel):
    name: str


class BoardOut(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ColumnCreate(BaseModel):
    title: str
    position: int = 0


class ColumnUpdate(BaseModel):
    title: str | None = None
    position: int | None = None


class ColumnOut(BaseModel):
    id: int
    title: str
    board_id: int
    position: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class CardCreate(BaseModel):
    title: str
    description: str | None = None
    tag: str | None = None
    column_id: int
    position: int | None = 0


class CardUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    tag: str | None = None
    column_id: int | None = None
    position: int | None = None
    assignee_id: int | None = None


class CardOut(BaseModel):
    id: int
    title: str
    description: str | None
    tag: str | None
    column_id: int
    position: int
    assignee_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
