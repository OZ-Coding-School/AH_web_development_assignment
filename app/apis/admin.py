from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.schemas.users import AdminUserRead, AdminUserRoleUpdate, Message
from app.services.user_service import UserService
from app.apis.deps import get_user_service, get_current_admin
from app.core.enums import Department

router = APIRouter(prefix="/admin/users", tags=["admin"])


@router.get("", response_model=List[AdminUserRead])
async def get_users(
    query: Optional[str] = Query(None, description="검색어 (이메일 혹은 이름)"),
    department: Optional[Department] = Query(None, description="부서 필터"),
    user_service: UserService = Depends(get_user_service),
    admin_user=Depends(get_current_admin),
):
    return await user_service.get_users_for_admin(query=query, department=department)


@router.patch("/role", response_model=Message)
async def update_user_role(
    role_update: AdminUserRoleUpdate,
    user_service: UserService = Depends(get_user_service),
    admin_user=Depends(get_current_admin),
):
    await user_service.update_user_role(role_update)
    return {"message": "회원 권한이 성공적으로 변경되었습니다."}
