import json

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


def _get_public_key(token: str):
    """Fetch Auth0 JWKS and return the RSA public key matching the token's kid."""
    try:
        header = jwt.get_unverified_header(token)
    except jwt.DecodeError:
        raise AuthenticationFailed("Invalid token header.")

    jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
    try:
        jwks = requests.get(jwks_url, timeout=5).json()
    except requests.RequestException:
        raise AuthenticationFailed("Unable to fetch JWKS.")

    for key in jwks.get("keys", []):
        if key.get("kid") == header.get("kid"):
            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))

    raise AuthenticationFailed("Public key not found in JWKS.")


def _fetch_userinfo(access_token: str) -> dict:
    """Fetch profile claims from Auth0 /userinfo endpoint using the access token."""
    url = f"https://{settings.AUTH0_DOMAIN}/userinfo"
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {access_token}"}, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return {}


def _get_or_create_user(payload: dict, access_token: str) -> User:
    """Get or create a Django User from an Auth0 JWT payload, syncing profile on first login."""
    sub = payload.get("sub")
    if not sub:
        raise AuthenticationFailed("Token missing 'sub' claim.")

    user, created = User.objects.get_or_create(
        auth0_sub=sub,
        defaults={"username": sub.replace("|", "_")},
    )

    # On first login, or whenever name/email are missing, fetch full profile from /userinfo
    needs_profile = created or not user.email or not user.first_name
    if needs_profile:
        profile = _fetch_userinfo(access_token)
        update_fields = []

        email = profile.get("email") or payload.get("email", "")
        if email and user.email != email:
            user.email = email
            update_fields.append("email")

        first_name = profile.get("given_name") or profile.get("name", "").split()[0] if profile.get("name") else ""
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            update_fields.append("first_name")

        last_name = profile.get("family_name", "")
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            update_fields.append("last_name")

        if update_fields:
            user.save(update_fields=update_fields)

    return user


class Auth0JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None  # Let other authenticators try

        token = auth_header.split(" ", 1)[1]
        public_key = _get_public_key(token)

        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=settings.AUTH0_AUDIENCE,
                issuer=settings.AUTH0_ISSUER,
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")
        except jwt.InvalidAudienceError:
            raise AuthenticationFailed("Invalid audience.")
        except jwt.InvalidIssuerError:
            raise AuthenticationFailed("Invalid issuer.")
        except jwt.DecodeError:
            raise AuthenticationFailed("Token decode error.")

        user = _get_or_create_user(payload, token)
        return (user, token)
