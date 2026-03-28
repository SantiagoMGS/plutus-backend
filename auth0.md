# Auth0 Integration — Backend (Django)

## Context

This Django project currently uses `djangorestframework-simplejwt` for JWT authentication with a custom `User` model (`apps/users/models.py`). The goal is to replace SimpleJWT with Auth0 token validation while keeping all existing business logic intact.

The auth flow after this change:
```
Auth0 (issues token) → Frontend (sends Bearer token) → Django (validates via JWKS) → request.user = Django User instance
```

Django continues to return `request.user` as a real Django `User` object (looked up or created on first login using the Auth0 `sub` claim). This keeps `OwnerFilterMixin` and all permission logic working without changes.

---

## Files to Modify

### 1. `requirements/base.txt`

Remove:
```
djangorestframework-simplejwt==5.5.1
```

Add:
```
pyjwt[crypto]>=2.9
requests>=2.32
```

---

### 2. `apps/users/models.py`

Add `auth0_sub` field to the `User` model to map Auth0 identities to Django users:

```python
class User(AbstractUser):
    currency_default = models.CharField(max_length=3, default="COP")
    auth0_sub = models.CharField(max_length=128, unique=True, null=True, blank=True)
```

After adding this field, generate and apply a migration:
```bash
python manage.py makemigrations users
python manage.py migrate
```

---

### 3. Create `apps/users/auth0_backend.py` (new file)

```python
import json
import requests
import jwt
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


def _get_or_create_user(payload: dict) -> User:
    """Get or create a Django User from an Auth0 JWT payload."""
    sub = payload.get("sub")
    if not sub:
        raise AuthenticationFailed("Token missing 'sub' claim.")

    user, created = User.objects.get_or_create(
        auth0_sub=sub,
        defaults={
            "username": sub.replace("|", "_"),  # auth0_provider_userid → safe username
            "email": payload.get("email", ""),
        },
    )

    # Sync email on every login in case it changed in Auth0
    if not created and payload.get("email") and user.email != payload["email"]:
        user.email = payload["email"]
        user.save(update_fields=["email"])

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

        user = _get_or_create_user(payload)
        return (user, token)
```

---

### 4. `config/settings/base.py`

**Remove** the entire `SIMPLE_JWT` block:
```python
# DELETE THIS BLOCK
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    ...
}
```

**Remove** `rest_framework_simplejwt` from `INSTALLED_APPS` (if present).

**Add** Auth0 settings (read from environment):
```python
import environ

env = environ.Env()

AUTH0_DOMAIN = env("AUTH0_DOMAIN")           # e.g. "yourapp.us.auth0.com"
AUTH0_AUDIENCE = env("AUTH0_AUDIENCE")       # e.g. "https://api.plutus.app"
AUTH0_ISSUER = f"https://{AUTH0_DOMAIN}/"   # trailing slash required
```

**Update** `REST_FRAMEWORK`:
```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.users.auth0_backend.Auth0JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # keep existing pagination and filter settings unchanged
}
```

---

### 5. `apps/users/urls.py`

**Remove** the SimpleJWT endpoints — Auth0 handles login and token refresh entirely:

```python
# DELETE these imports and URL patterns:
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# path("login/", TokenObtainPairView.as_view(), name="login"),
# path("refresh/", TokenRefreshView.as_view(), name="refresh"),
```

**Keep**:
```python
urlpatterns = [
    path("me/", ProfileView.as_view(), name="profile"),
    # Remove register/ and change-password/ — handled by Auth0
]
```

> **Note:** Registration, password reset, and social login are now managed by Auth0 Universal Login. Remove `RegisterView` and `ChangePasswordView` from `views.py` as well.

---

### 6. `apps/users/views.py`

**Remove**: `RegisterView`, `ChangePasswordView`
**Keep**: `ProfileView` (GET/PATCH `/api/auth/me/`)

The `ProfileView` continues to work as-is since `request.user` is still a Django `User` object.

---

### 7. `apps/users/services.py`

**Remove**: `UserService.register_user()`, `UserService.change_password()`
**Keep**: `UserService.update_profile()` — used by `ProfileView`

---

### 8. `.env` / `.env.example`

Add the following variables:
```env
AUTH0_DOMAIN=yourapp.us.auth0.com
AUTH0_AUDIENCE=https://api.plutus.app
```

Remove (no longer needed):
```env
# SECRET_KEY is still needed for Django internals — keep it
```

---

## Auth0 Dashboard Setup (do this first)

1. **Create an API**:
   - Dashboard → Applications → APIs → Create API
   - Name: `Plutus API`
   - Identifier: `https://api.plutus.app` (this becomes `AUTH0_AUDIENCE`)
   - Signing Algorithm: **RS256**
   - Enable **Allow Offline Access** (for refresh tokens)

2. **Create a SPA Application**:
   - Dashboard → Applications → Create Application → Single Page Application
   - Name: `Plutus Frontend`
   - Allowed Callback URLs: `http://localhost:5173, https://yourdomain.com`
   - Allowed Logout URLs: `http://localhost:5173, https://yourdomain.com`
   - Allowed Web Origins: `http://localhost:5173, https://yourdomain.com`

3. **Enable Refresh Token Rotation** on the SPA application settings.

---

## What Does NOT Change

- `common/mixins.py` — `OwnerFilterMixin` uses `request.user`, which is still a Django User object.
- All business logic in `accounts`, `categories`, `transactions` apps.
- `common/pagination.py`
- `config/urls.py` (except the removed auth endpoints)
- Database schema for all non-user models.

---

## Testing After Implementation

```bash
# 1. Get a token from Auth0 (use Auth0 dashboard "Test" tab on your API)
# 2. Test a protected endpoint
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/auth/me/

# 3. Test that unauthenticated requests are rejected
curl http://localhost:8000/api/accounts/  # should return 401
```
