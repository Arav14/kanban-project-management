from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

# Auth

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
    model_config = {"from_attributes": True}


# Board

class BoardCreate(BaseModel):
    name: str

class BoardOut(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime
    model_config = {"from_attributes": True}


# Column

class ColumnCreate(BaseModel):
    title: str
    position: int = 0

class ColumnUpdate(BaseModel):
    title: Optional[str] = None
    position: Optional[str] = None

class ColumnOut(BaseModel):
    id: int
    title: str
    board_id: int
    position: int
    model_config = {"from_attributes": True}


# Card

class CardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    tag: Optional[str] = None
    column_id: int
    position: Optional[int] = 0

class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    column_id: Optional[int] = None
    position: Optional[int] = None
    assignee_id: Optional[int] = None

class CardOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    tag: Optional[str]
    column_id: int
    position: int
    assignee_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

