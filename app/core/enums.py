from enum import StrEnum


class UserRole(StrEnum):
    PENDING = "pending"
    STAFF = "staff"
    ADMIN = "admin"


class Gender(StrEnum):
    M = "male"
    F = "female"


class Department(StrEnum):
    DEV = "developer"  # 개발자
    MEDICAL = "medical team"  # 의료진
    RESEARCH = "researcher"  # 연구진
