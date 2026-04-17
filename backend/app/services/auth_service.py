from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token

class AuthService:

    @staticmethod
    async def register(data: RegisterRequest, db: AsyncSession) -> TokenResponse:
        # Check of email already taken
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code = 400, detail = "Email already registered")

        user = User(email = data.email, full_name = data.full_name, password_hash = hash_password(data.password))
        db.add(user)
        await db.flush() # get user.id without full commit

        return TokenResponse(access_token = create_access_token({"sub": str(user.id)}), refresh_token = create_refresh_token({"sub": str(user.id)}))

    @staticmethod
    async def login(data, db):

        # 🔥 get user directly from DB
        result = await db.execute(
            select(User).where(User.email == data.email)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }