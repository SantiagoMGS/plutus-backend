from __future__ import annotations

from .models import User


class UserService:
    @staticmethod
    def update_profile(user: User, validated_data: dict) -> User:
        for field, value in validated_data.items():
            setattr(user, field, value)
        user.save(update_fields=validated_data.keys())
        return user

    @staticmethod
    def save_document_metadata(user: User, document_type: str, document_number: str) -> User:
        """Save document info locally."""
        user.document_type = document_type
        user.document_number = document_number
        user.save(update_fields=["document_type", "document_number"])
        return user

    @staticmethod
    def delete_account(user: User) -> None:
        """Deactivate user locally."""
        user.is_active = False
        user.save(update_fields=["is_active"])
