import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

# Initialize Firebase Admin SDK once at module load
if not firebase_admin._apps:
    if hasattr(settings, "FIREBASE_CREDENTIALS_PATH") and settings.FIREBASE_CREDENTIALS_PATH:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
    else:
        # Uses GOOGLE_APPLICATION_CREDENTIALS env var or Application Default Credentials
        firebase_admin.initialize_app()


def _get_or_create_user(decoded_token: dict) -> User:
    """Get or create a Django User from a decoded Firebase ID token."""
    uid = decoded_token.get("uid")
    if not uid:
        raise AuthenticationFailed("Token missing 'uid'.")

    user, created = User.objects.get_or_create(
        firebase_uid=uid,
        defaults={"username": uid},
    )

    if created or not user.email or not user.first_name:
        update_fields = []

        email = decoded_token.get("email", "")
        if email and user.email != email:
            user.email = email
            update_fields.append("email")

        name = decoded_token.get("name", "")
        if name:
            parts = name.split(maxsplit=1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""

            if first_name and user.first_name != first_name:
                user.first_name = first_name
                update_fields.append("first_name")
            if last_name and user.last_name != last_name:
                user.last_name = last_name
                update_fields.append("last_name")

        if update_fields:
            user.save(update_fields=update_fields)

    return user


class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ", 1)[1]

        try:
            decoded_token = firebase_auth.verify_id_token(token)
        except firebase_auth.ExpiredIdTokenError:
            raise AuthenticationFailed("Token has expired.")
        except firebase_auth.RevokedIdTokenError:
            raise AuthenticationFailed("Token has been revoked.")
        except firebase_auth.InvalidIdTokenError:
            raise AuthenticationFailed("Invalid token.")
        except Exception:
            raise AuthenticationFailed("Token verification failed.")

        user = _get_or_create_user(decoded_token)
        return (user, decoded_token)
