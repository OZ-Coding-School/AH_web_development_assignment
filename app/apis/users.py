from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.users import UserCreate, UserLogin, Token, UserRead, UserUpdate, Message
from app.services.user_service import UserService
from app.apis.deps import get_user_service, get_current_user
from app.models.users import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=Message, status_code=status.HTTP_201_CREATED)
async def signup(user_create: UserCreate, user_service: UserService = Depends(get_user_service)):
    await user_service.signup(user_create)
    return {"message": "회원가입이 완료되었습니다."}


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
):
    # form_data.username을 email로 사용하여 로그인 처리
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    return await user_service.login(user_login)


@router.post("/logout", response_model=Message)
async def logout(current_user: User = Depends(get_current_user)):
    # JWT 방식에서는 서버측 로그아웃 처리가 필수는 아니지만, 블랙리스트 등을 구현할 수 있습니다.
    # 명세서에 따라 성공 메시지를 반환합니다.
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


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: User = Depends(get_current_user), user_service: UserService = Depends(get_user_service)
):
    await user_service.delete_me(current_user.id)
    return None
