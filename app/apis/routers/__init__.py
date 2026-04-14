from .admin import router as admin_router
from .medical_records import router as medical_record_router
from .users import router as user_router
from .patients import router as patient_router
from .practice_apis import practice_router

__all__ = [
    "admin_router",
    "medical_record_router",
    "user_router",
    "patient_router",
    "practice_router",
]
