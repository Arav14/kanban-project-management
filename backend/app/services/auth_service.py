from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)


class AuthService:
    @staticmethod
    async def register(
        data: RegisterRequest,
        db: AsyncSession,
    ) -> TokenResponse:
        result = await db.execute(
            select(User).where(User.email == data.email)
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )

        user = User(
            email=data.email,
            full_name=data.full_name,
            password_hash=hash_password(data.password),
        )

        db.add(user)
        await db.flush()

        return TokenResponse(
            access_token=create_access_token(
                {"sub": str(user.id)}
            ),
            refresh_token=create_refresh_token(
                {"sub": str(user.id)}
            ),
        )

    @staticmethod
    async def login(
        data: LoginRequest,
        db: AsyncSession,
    ) -> TokenResponse:
        result = await db.execute(
            select(User).where(User.email == data.email)
        )

        user = result.scalar_one_or_none()

        if not user or not verify_password(
            data.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return TokenResponse(
            access_token=create_access_token(
                {"sub": str(user.id)}
            ),
            refresh_token=create_refresh_token(
                {"sub": str(user.id)}
            ),
        )
