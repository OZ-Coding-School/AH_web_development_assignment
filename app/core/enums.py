from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"


class Gender(StrEnum):
    M = "male"
    F = "female"
