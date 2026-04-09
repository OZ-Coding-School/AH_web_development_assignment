import re
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr, AfterValidator


user_list = [
    {
        "id": 1,
        "name": "홍길동",
        "age": 24,
        "email": "gildong24@example.com",
        "password": "Password1234!!",
    },
    {
        "id": 2,
        "name": "장문복",
        "age": 21,
        "email": "moonluck12@example.com",
        "password": "Check1321!",
    },
    {
        "id": 3,
        "name": "임우진",
        "age": 31,
        "email": "limousine33@example.com",
        "password": "lwsPAssword12@",
    },
]

practice_router = APIRouter(prefix="/practice_api/users", tags=["Practice"])


def validate_password(value: Optional[str]) -> Optional[str]:
    # None일때 그대로 리턴
    if value is None:
        return value

    # 8글자 이상인지 검증
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    # 대문자가 포함되어 있는지 검증
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must include an uppercase letter")

    # 소문자가 포함되어 있는지 검증
    if not re.search(r"[a-z]", value):
        raise ValueError("Password must include an lowercase letter")

    # 숫자가 포함되어 있는지 검증
    if not re.search(r"[0-9]", value):
        raise ValueError("Password must include a number")

    # 특수문자가 포함되어 있는지 검증
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        raise ValueError("Password must include a special character")

    return value


class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    email: str


class UserCreateRequest(BaseModel):
    name: str
    age: int
    email: EmailStr
    password: Annotated[str, AfterValidator(validate_password)]


UpdatePasswordType = Annotated[str | None, AfterValidator(validate_password)]


class UserUpdateRequest(BaseModel):
    age: int | None = Field(None, ge=14)
    email: EmailStr | None = Field(None, max_length=30)
    password: UpdatePasswordType = None


@practice_router.get("", status_code=200)
async def get_user_list() -> list[UserResponse]:
    return [UserResponse.model_validate(user) for user in user_list]


@practice_router.post("", status_code=201)
async def create_user(user_info: UserCreateRequest) -> UserResponse:
    is_duplicated_email = any(user["email"] == user_info.email for user in user_list)
    # 이미 존재하는 이메일이면
    if is_duplicated_email:
        # 409 Conflict 응답으로 반환
        raise HTTPException(status_code=409, detail="Email already exists.")
    user_data = user_info.model_dump()
    # 유저 id를 자동증분된 값으로 추가
    user_data["id"] = len(user_list) + 1
    user_list.append(user_data)
    return UserResponse.model_validate(user_data)


@practice_router.get("/{user_id}", status_code=200)
async def get_user_detail(user_id: int) -> UserResponse:
    user = next((user for user in user_list if user["id"] == user_id), None)
    # 유저가 목록에 존재하지 않으면
    if not user:
        # 404 NotFound 발생
        raise HTTPException(status_code=404, detail="User not found.")
    return UserResponse.model_validate(user)


@practice_router.patch("/{user_id}", status_code=200)
async def partial_update_user(
    user_id: int, user_info: UserUpdateRequest
) -> UserResponse:
    # 유저리스트에서 해당 user_id의 유저 정보가 존재하는지 확인
    user = next((user for user in user_list if user["id"] == user_id), None)
    # 유저가 존재하지 않으면
    if not user:
        # 404 NotFound 발생
        raise HTTPException(status_code=404, detail="User not found.")
    user_data = user_info.model_dump(exclude_unset=True)
    # 업데이트 데이터가 없으면
    if not user_data:
        # 400 Bad Request 응답으로 반환
        raise HTTPException(
            status_code=400, detail="At least one field must be provided for update."
        )
    # 업데이트 데이터에 이메일이 존재하면
    if "email" in user_data:
        # 유저 리스트에서 중복 여부 검사
        if any(
            u["email"] == user_data["email"] and u["id"] != user_id for u in user_list
        ):
            # 중복이면 409 Conflict 응답으로 반환
            raise HTTPException(status_code=409, detail="Email already exists.")
    user.update(user_data)
    return UserResponse.model_validate(user)


@practice_router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int) -> None:
    user = next((user for user in user_list if user["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user_list.remove(user)
