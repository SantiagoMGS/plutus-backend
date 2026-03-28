from __future__ import annotations

from .models import User


class UserService:
    @staticmethod
    def update_profile(user: User, validated_data: dict) -> User:
        for field, value in validated_data.items():
            setattr(user, field, value)
        user.save(update_fields=validated_data.keys())
        return user
