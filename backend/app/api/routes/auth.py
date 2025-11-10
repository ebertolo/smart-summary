"""
Authentication routes
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.models.schemas import Token, UserLogin
from app.services.user_service import authenticate_user

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and get JWT access token.

    **Demo Credentials:**
    - Username: `demo`
    - Password: `demo123`

    **Returns:**
    - `access_token`: JWT token for authentication
    - `token_type`: Always "bearer"
    - `expires_in`: Token validity in seconds (default: 3600s)

    **Usage:**
    Use the returned token in the Authorization header:
    ```
    Authorization: Bearer <access_token>
    ```
    """
    user = await authenticate_user(db, user_data.username, user_data.password)

    if not user:
        print(
            f"[AUTH] Login failed - invalid credentials for user: {user_data.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    print(f"[AUTH] Login successful - user: {user.username}")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRATION_MINUTES * 60,
    }


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.

    **Authentication Required:** Yes (Bearer token)

    **Returns:**
    - Username of authenticated user
    - Success confirmation message

    **Note:** This endpoint is useful to verify token validity.
    """
    return {
        "username": current_user["username"],
        "message": "Authenticated successfully",
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout endpoint for logging purposes.

    **Authentication Required:** Yes (Bearer token)

    **Returns:**
    - Logout confirmation message

    **Note:** JWT tokens are stateless, so actual invalidation happens client-side.
    This endpoint is primarily for logging and potential future token blacklisting.
    """
    print(f"[AUTH] Logout - user: {current_user['username']}")

    return {"message": "Logged out successfully", "username": current_user["username"]}
