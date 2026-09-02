from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from auth import (
    create_access_token,
    create_password_reset_token,
    get_current_user,
    verify_password,
    verify_password_reset_token,
)
from models import (
    AuthMeResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
)
from stores import profile_store
from user_service import change_password, get_user_by_email, set_user_password

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


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest) -> JSONResponse:
    generic_message = {
        "message": "Si el email existe, se generó un enlace de recuperación.",
    }

    user = get_user_by_email(payload.email)
    if user is None:
        # No revelamos si el email existe para evitar enumeracion de cuentas.
        return JSONResponse(content=generic_message)

    reset_token, expires_in = create_password_reset_token(user_id=user["id"])

    # No hay servicio de envio de email configurado en este proyecto:
    # el token se devuelve directamente para permitir completar el flujo end-to-end.
    return JSONResponse(
        content={
            **generic_message,
            "reset_token": reset_token,
            "expires_in": expires_in,
        }
    )


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest) -> JSONResponse:
    user_id = verify_password_reset_token(payload.token)
    updated = set_user_password(user_id=user_id, new_password=payload.new_password)
    if updated is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return JSONResponse(content={"message": "Contraseña actualizada correctamente"})


@router.post("/change-password")
def change_password_route(
    payload: ChangePasswordRequest, current_user: dict = Depends(get_current_user)
) -> JSONResponse:
    change_password(
        user_id=current_user["id"],
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return JSONResponse(content={"message": "Contraseña actualizada correctamente"})
