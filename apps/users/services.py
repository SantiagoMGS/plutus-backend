from __future__ import annotations

import requests
from django.conf import settings

from .models import User


class UserService:
    @staticmethod
    def update_profile(user: User, validated_data: dict) -> User:
        for field, value in validated_data.items():
            setattr(user, field, value)
        user.save(update_fields=validated_data.keys())
        return user

    @staticmethod
    def _get_mgmt_token() -> str:
        """Obtain a Management API access token using client credentials."""
        url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "audience": f"https://{settings.AUTH0_DOMAIN}/api/v2/",
        }
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()["access_token"]

    @staticmethod
    def save_document_metadata(user: User, document_type: str, document_number: str) -> User:
        """Save document info locally and as Auth0 user_metadata."""
        # Save locally
        user.document_type = document_type
        user.document_number = document_number
        user.save(update_fields=["document_type", "document_number"])

        # Save to Auth0 user_metadata
        if user.auth0_sub and settings.AUTH0_CLIENT_ID:
            mgmt_token = UserService._get_mgmt_token()
            url = f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{user.auth0_sub}"
            requests.patch(
                url,
                json={
                    "user_metadata": {
                        "document_type": document_type,
                        "document_number": document_number,
                    }
                },
                headers={"Authorization": f"Bearer {mgmt_token}"},
                timeout=10,
            )

        return user

    @staticmethod
    def delete_account(user: User) -> None:
        """Deactivate user locally and block in Auth0."""
        user.is_active = False
        user.save(update_fields=["is_active"])

        if user.auth0_sub and settings.AUTH0_CLIENT_ID:
            mgmt_token = UserService._get_mgmt_token()
            url = f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{user.auth0_sub}"
            requests.patch(
                url,
                json={"blocked": True},
                headers={"Authorization": f"Bearer {mgmt_token}"},
                timeout=10,
            )
