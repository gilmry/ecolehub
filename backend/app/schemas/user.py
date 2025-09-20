from enum import Enum


class UserRole(str, Enum):
    PARENT = "parent"
    ADMIN = "admin"
    DIRECTION = "direction"
    TEACHER = "teacher"
