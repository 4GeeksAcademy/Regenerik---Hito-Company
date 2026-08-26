from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from auth import create_access_token, get_current_user, verify_password
from models import AuthMeResponse, LoginRequest, LoginResponse
from stores import profile_store
from user_service import get_user_by_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> JSONResponse:
    user = get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token, expires_in = create_access_token(user_id=user["id"])
    return JSONResponse(
        content={
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "user_id": user["id"],
        }
    )


@router.get("/me", response_model=AuthMeResponse)
def auth_me(current_user: dict = Depends(get_current_user)) -> JSONResponse:
    profile = profile_store.get_by_user_id(current_user["id"])
    return JSONResponse(
        content={
            "id": current_user["id"],
            "email": current_user["email"],
            "role": current_user["role"],
            "profile": profile,
        }
    )
