"""Compatibility shim for tests importing app.models.user.User.

Maps to Stage 1 SQLAlchemy User model while accepting extra kwargs like 'role'.
"""
from typing import Any

from app.models_stage1 import User as SAUser


def User(**kwargs: Any) -> SAUser:  # type: ignore
    # Drop unsupported/optional fields for compatibility
    kwargs.pop("role", None)
    return SAUser(**kwargs)
