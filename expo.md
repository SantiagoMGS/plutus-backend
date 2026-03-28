# Exposición — Integración Auth0 (Backend)

## Contexto

Plutus es una API REST de finanzas personales construida con Django REST Framework. El sistema de autenticación fue migrado de credenciales propias (usuario/contraseña gestionados por Django) a Auth0, un proveedor de identidad externo. Esto delega completamente el login, registro y gestión de contraseñas a Auth0, y el backend se limita a **validar tokens y conocer al usuario**.

---

## Flujo general de autenticación

```
Usuario  →  Frontend (Expo/React Native)  →  Auth0
                                               ↓ emite Access Token (JWT)
Frontend  →  Django API  (Authorization: Bearer <token>)
                ↓
         Valida el token via JWKS
                ↓
         Busca o crea el usuario en la BD
                ↓
         request.user = instancia Django User
                ↓
         Responde normalmente
```

El backend **nunca ve la contraseña** del usuario. Solo recibe y valida el token que Auth0 emitió.

---

## Componentes implementados

### 1. Campo `auth0_sub` en el modelo User
**Archivo:** `apps/users/models.py`

```python
auth0_sub = models.CharField(max_length=128, unique=True, null=True, blank=True)
```

Cada usuario de Auth0 tiene un identificador único llamado `sub` (subject), con formato `google-oauth2|1056907009...` o `auth0|abc123`. Este campo es la "llave" que conecta una identidad de Auth0 con un usuario de Django. Es único, garantizando que no se creen duplicados aunque el usuario inicie sesión múltiples veces.

---

### 2. Backend de autenticación personalizado
**Archivo:** `apps/users/auth0_backend.py`

Este archivo contiene toda la lógica de validación. Tiene tres funciones:

#### `_get_public_key(token)`
Auth0 firma sus tokens con una clave privada RSA. Para verificar que el token no fue falsificado, necesitamos la clave pública correspondiente. Auth0 la publica en una URL estándar llamada **JWKS** (JSON Web Key Set):

```
https://plutus-dev-col.us.auth0.com/.well-known/jwks.json
```

La función descarga esas claves, encuentra la que corresponde al token (usando el campo `kid` del header del JWT), y retorna la clave pública RSA lista para verificar la firma.

#### `_fetch_userinfo(access_token)`
Los Access Tokens de Auth0 orientados a una API externa (como la nuestra) **no incluyen datos de perfil** como nombre o email — solo el `sub`. Para obtener esos datos se llama al endpoint estándar de OpenID Connect:

```
https://plutus-dev-col.us.auth0.com/userinfo
```

Este endpoint responde con el perfil completo: `email`, `given_name`, `family_name`, `name`, etc.

#### `_get_or_create_user(payload, access_token)`
Con el `sub` del token, busca si ya existe un usuario Django con ese `auth0_sub`. Si no existe, lo crea (primer login). Luego, si faltan datos de perfil (email, nombre), llama a `/userinfo` y sincroniza los campos. Esto garantiza que:
- El primer login crea el usuario automáticamente
- Los datos de perfil siempre se sincronizan con lo que Auth0 tiene
- Logins subsiguientes con perfil completo no hacen requests extras (sin latencia innecesaria)

#### `Auth0JWTAuthentication` (clase principal)
Implementa la interfaz `BaseAuthentication` de Django REST Framework. DRF llama a su método `authenticate(request)` en cada request:

1. Lee el header `Authorization: Bearer <token>`
2. Obtiene la clave pública via JWKS
3. Decodifica y verifica el JWT (algoritmo RS256, audience, issuer)
4. Llama a `_get_or_create_user` para obtener el usuario Django
5. Retorna `(user, token)` → DRF pone el usuario en `request.user`

Si el token expiró, tiene un audience incorrecto o fue manipulado, lanza `AuthenticationFailed` con el error correspondiente.

---

### 3. Configuración en Django
**Archivo:** `config/settings/base.py`

```python
AUTH0_DOMAIN   = "plutus-dev-col.us.auth0.com"
AUTH0_AUDIENCE = "https://api.plutus.app"
AUTH0_ISSUER   = "https://plutus-dev-col.us.auth0.com/"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.users.auth0_backend.Auth0JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    ...
}
```

Al registrar `Auth0JWTAuthentication` como la clase de autenticación por defecto, **todos los endpoints** del sistema pasan automáticamente por esta validación sin necesidad de cambiar ninguna vista existente.

---

### 4. Endpoint de perfil
**Archivo:** `apps/users/views.py`

El único endpoint de autenticación que queda en el backend es:

```
GET  /api/auth/me/   → devuelve el perfil del usuario autenticado
PATCH /api/auth/me/  → actualiza campos editables (first_name, last_name, currency_default)
```

Login, registro y cambio de contraseña ya no existen en el backend — son responsabilidad de Auth0.

---

## Por qué este diseño

| Decisión | Alternativa descartada | Razón |
|---|---|---|
| Validar el token localmente via JWKS | Llamar a Auth0 en cada request para validar | Mucho más rápido; no hay dependencia de red para validar |
| Guardar `auth0_sub` en la BD | No guardar nada y solo usar Auth0 | Necesitamos FKs reales en Django para cuentas, transacciones, etc. |
| Llamar a `/userinfo` solo cuando faltan datos | Siempre o nunca | Balance entre datos frescos y no agregar latencia a cada request |
| RS256 (clave pública/privada) | HS256 (secreto compartido) | Auth0 usa RS256 por defecto; más seguro porque el secreto nunca sale de Auth0 |

---

## Conceptos clave para la exposición

- **JWT (JSON Web Token):** token firmado digitalmente que contiene claims (sub, email, exp, etc.). No requiere consultar una BD para validarlo.
- **RS256:** algoritmo de firma asimétrico. Auth0 firma con su clave privada; cualquiera puede verificar con la clave pública (JWKS).
- **JWKS:** endpoint estándar donde Auth0 publica sus claves públicas.
- **`sub` claim:** identificador único e inmutable del usuario en Auth0. Es la fuente de verdad para la identidad.
- **Access Token vs ID Token:** el Access Token es para llamar a la API (lo que recibe el backend); el ID Token es para que el frontend conozca el perfil. Por eso necesitamos `/userinfo` en el backend.
- **`get_or_create`:** patrón de Django que busca un registro por un campo único y lo crea si no existe, en una sola operación atómica.
