from fastapi import APIRouter, Depends, status, Response, Cookie, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.users import (
    UserCreate,
    UserLogin,
    Token,
    UserRead,
    UserUpdate,
    PasswordUpdate,
    Message,
    AccessToken,
)
from app.services.user_service import UserService
from app.apis.deps import get_user_service, get_current_user
from app.models.users import User
from app.core.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=Message, status_code=status.HTTP_201_CREATED)
async def signup(user_create: UserCreate, user_service: UserService = Depends(get_user_service)):
    await user_service.signup(user_create)
    return {"message": "회원가입이 완료되었습니다."}


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
):
    # form_data.username을 email로 사용하여 로그인 처리
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    tokens = await user_service.login(user_login)

    # 리프레시 토큰을 HTTP-only 쿠키로 설정
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="strict",
    )

    return {"access_token": tokens["access_token"], "token_type": "bearer"}


@router.post("/refresh", response_model=AccessToken)
async def refresh_token(
    refresh_token: str = Cookie(None),
    user_service: UserService = Depends(get_user_service),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 필요합니다.",
        )
    access_token = await user_service.refresh_access_token(refresh_token)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", response_model=Message)
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    response.delete_cookie(key="refresh_token")
    return {"message": "성공적으로 로그아웃되었습니다."}


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=Message)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    await user_service.update_me(current_user.id, user_update)
    return {"message": "회원 정보가 수정되었습니다."}


@router.patch("/me/password", response_model=Message)
async def update_password(
    password_update: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    await user_service.update_password(current_user.id, password_update)
    return {"message": "비밀번호가 변경되었습니다."}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: User = Depends(get_current_user), user_service: UserService = Depends(get_user_service)
):
    await user_service.delete_me(current_user.id)
    return None
