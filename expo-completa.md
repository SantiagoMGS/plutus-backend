# Exposición — Autenticación con Auth0 en Plutus (Frontend + Backend)

## ¿Qué es Plutus y cuál era el problema?

Plutus es una aplicación de finanzas personales compuesta por un **frontend en React (Vite)** y una **API REST en Django**. Antes de esta implementación, el sistema de autenticación era propio: el backend almacenaba contraseñas, emitía sus propios JWT con SimpleJWT y exponía endpoints de registro, login y cambio de contraseña.

Esto fue reemplazado por **Auth0**, un proveedor de identidad como servicio (IDaaS), que delega toda la responsabilidad de autenticación a un servicio especializado. El resultado: el backend nunca ve contraseñas, el frontend nunca gestiona tokens manualmente, y se obtiene soporte para Google login sin código adicional.

---

## Arquitectura general

```
┌─────────────────────────────────────────────────────────────────┐
│                        AUTH0                                    │
│   plutus-dev-col.us.auth0.com                                   │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │ Universal    │    │  Emite       │    │ JWKS público     │   │
│  │ Login UI     │    │  Tokens JWT  │    │ /.well-known/    │   │
│  │ (Google,     │    │  (RS256)     │    │ jwks.json        │   │
│  │  email/pass) │    │              │    │                  │   │
│  └──────────────┘    └──────────────┘    └──────────────────┘   │
└────────────┬──────────────────┬──────────────────┬──────────────┘
             │                  │                  │
             │ redirige         │ emite tokens     │ clave pública
             ▼                  ▼                  ▼
┌────────────────────┐    ┌──────────────────────────────────────┐
│     FRONTEND       │    │           BACKEND (Django)           │
│  React + Vite      │    │                                      │
│                    │    │  Auth0JWTAuthentication               │
│  @auth0/auth0-react│───▶│  - valida firma RS256 via JWKS       │
│  Authorization:    │    │  - verifica audience + issuer        │
│  Bearer <token>    │    │  - busca/crea usuario por auth0_sub  │
│                    │    │  - pone user en request.user         │
└────────────────────┘    └──────────────────────────────────────┘
```

---

## Protocolo: OAuth 2.0 + PKCE

El flujo usa **Authorization Code Flow con PKCE** (Proof Key for Code Exchange), el estándar recomendado para aplicaciones web públicas (SPA).

### ¿Por qué PKCE y no un secreto de cliente?

Las SPAs no pueden guardar un `client_secret` de forma segura — cualquiera puede inspeccionar el código fuente o el bundle en el navegador. PKCE resuelve esto sin necesitar un secreto.

### Cómo funciona:

1. El frontend genera un `code_verifier` (string aleatorio de 128 caracteres)
2. Calcula `code_challenge = base64url(SHA256(code_verifier))`
3. Redirige al usuario a Auth0 enviando el `code_challenge` (visible, no es secreto)
4. El usuario se autentica en Auth0 Universal Login
5. Auth0 devuelve un `code` temporal a `http://localhost:5173?code=...`
6. El SDK canjea `code` + `code_verifier` por los tokens
7. Auth0 verifica: `SHA256(code_verifier) == code_challenge` → solo la app original puede canjearlo

El SDK de `@auth0/auth0-react` hace todo esto automáticamente.

---

## Flujo completo paso a paso

```
1. Usuario abre Plutus y navega a /accounts (ruta protegida)
          │
          ▼
2. ProtectedRoute detecta isAuthenticated = false
          │
          ▼
3. Redirige a /login → LoginPage llama loginWithRedirect()
          │
          ▼
4. Navegador va a Auth0 Universal Login
   (plutus-dev-col.us.auth0.com/authorize?
    code_challenge=...&audience=https://api.plutus.app&scope=openid profile email)
          │
          ▼
5. Usuario ingresa credenciales (o usa Google)
          │
          ▼
6. Auth0 redirige de vuelta: http://localhost:5173?code=ABC&state=XYZ
          │
          ▼
7. SDK intercambia code + code_verifier → obtiene tokens:
   - access_token  (1h de vida, para llamar a la API)
   - refresh_token (renovación silenciosa)
   - id_token      (perfil del usuario para el frontend)
          │
          ▼
8. Tokens guardados en localStorage. isAuthenticated = true
          │
          ▼
9. ProtectedRoute renderiza /accounts
          │
          ▼
10. Frontend hace request: GET /api/accounts/
    Header: Authorization: Bearer <access_token>
          │
          ▼
11. Django recibe el request → Auth0JWTAuthentication.authenticate()
          │
          ├─ Descarga clave pública desde JWKS de Auth0
          ├─ Verifica firma RS256, audience (https://api.plutus.app), issuer
          ├─ Extrae claim sub = "google-oauth2|1056907009..."
          ├─ Busca User donde auth0_sub = sub
          │     SI no existe → lo crea + llama /userinfo para obtener email y nombre
          │     SI existe y tiene datos → continúa sin requests extra
          └─ Pone el usuario en request.user
          │
          ▼
12. Django filtra cuentas por request.user y responde con JSON
          │
          ▼
13. Frontend muestra las cuentas del usuario
```

---

## Implementación — Frontend

### `src/main.tsx` — Punto de entrada

```tsx
<Auth0Provider
  domain={import.meta.env.VITE_AUTH0_DOMAIN}
  clientId={import.meta.env.VITE_AUTH0_CLIENT_ID}
  authorizationParams={{
    redirect_uri: window.location.origin,
    audience: import.meta.env.VITE_AUTH0_AUDIENCE,  // "https://api.plutus.app"
    scope: "openid profile email",
  }}
  useRefreshTokens={true}
  cacheLocation="localstorage"
>
```

`audience` le indica a Auth0 para qué API se pide el token. Si se omite, Auth0 emite un token opaco que el backend no puede validar. `scope: "openid profile email"` solicita que `/userinfo` tenga disponibles los datos de perfil.

`useRefreshTokens + cacheLocation="localstorage"` habilita renovación silenciosa de tokens sin depender de cookies de terceros (bloqueadas en navegadores modernos).

### `src/components/protected-route.tsx` — Control de acceso

```tsx
const { isAuthenticated, isLoading } = useAuth0();

if (isLoading) return <Spinner />;              // Auth0 restaurando sesión desde localStorage
if (!isAuthenticated) return <Navigate to="/login" />;
return <Outlet />;
```

`isLoading` es crítico: evita redirigir al login mientras Auth0 está leyendo los tokens del storage al recargar la página. Sin este estado, el usuario autenticado siempre sería expulsado en cada recarga.

### `src/hooks/use-api-auth.ts` — Puente entre Auth0 y Axios

```tsx
const { getAccessTokenSilently, isAuthenticated } = useAuth0();

useEffect(() => {
  if (isAuthenticated) {
    setTokenGetter(() => getAccessTokenSilently({
      authorizationParams: { audience: import.meta.env.VITE_AUTH0_AUDIENCE }
    }));
  }
}, [isAuthenticated, getAccessTokenSilently]);
```

Registra `getAccessTokenSilently` como la función que el interceptor de Axios llamará en cada request. Si el `access_token` expiró, el SDK lo renueva automáticamente usando el `refresh_token` antes de retornar.

### `src/api/client.ts` — Interceptor de Axios

```typescript
apiClient.interceptors.request.use(async (config) => {
  if (getTokenFn) {
    const token = await getTokenFn();  // getAccessTokenSilently()
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

Cada request HTTP a Django se intercepta aquí. El token siempre está vigente porque `getAccessTokenSilently` hace refresh si es necesario — el frontend nunca envía un token expirado.

---

## Implementación — Backend

### `apps/users/models.py` — Campo `auth0_sub`

```python
auth0_sub = models.CharField(max_length=128, unique=True, null=True, blank=True)
```

El `sub` es el identificador único e inmutable del usuario en Auth0 (ej: `google-oauth2|1056907009...`). Es la llave que vincula una identidad de Auth0 con un registro Django. Sin este campo, cada login podría crear un usuario duplicado.

### `apps/users/auth0_backend.py` — Validación del token

**`_get_public_key(token)`**

Auth0 firma los tokens con su clave privada RSA. Para verificar que el token es auténtico y no fue falsificado, se necesita la clave pública. Auth0 la publica en el endpoint estándar JWKS:

```
https://plutus-dev-col.us.auth0.com/.well-known/jwks.json
```

El token tiene en su header un campo `kid` (key ID) que identifica cuál de las claves del JWKS usó Auth0 para firmar. La función descarga las claves, encuentra la que coincide con el `kid`, y retorna la clave pública RSA.

**`_fetch_userinfo(access_token)`**

El Access Token de Auth0 orientado a una API externa contiene solo el `sub` — no incluye email ni nombre. Esto es por diseño: el token de acceso es para autorizar, no para transmitir perfil. Para obtener los datos de perfil se llama al endpoint estándar de OpenID Connect con el mismo token:

```
https://plutus-dev-col.us.auth0.com/userinfo
→ { "email": "...", "given_name": "...", "family_name": "..." }
```

**`_get_or_create_user(payload, access_token)`**

```python
user, created = User.objects.get_or_create(
    auth0_sub=sub,
    defaults={"username": sub.replace("|", "_")},
)

needs_profile = created or not user.email or not user.first_name
if needs_profile:
    profile = _fetch_userinfo(access_token)
    # sincroniza email, first_name, last_name
```

`get_or_create` es una operación atómica: si el usuario no existe lo crea, si existe lo retorna — sin race conditions. El fetch a `/userinfo` solo ocurre cuando faltan datos, para no agregar latencia a requests normales.

**`Auth0JWTAuthentication.authenticate(request)`**

```python
payload = jwt.decode(
    token,
    public_key,
    algorithms=["RS256"],
    audience=settings.AUTH0_AUDIENCE,
    issuer=settings.AUTH0_ISSUER,
)
```

Verifica tres cosas simultáneamente:
- **Firma**: el token fue firmado por Auth0 (con su clave privada) y no fue alterado
- **Audience**: el token fue emitido para esta API (`https://api.plutus.app`), no para otra
- **Issuer**: el token viene del tenant correcto (`plutus-dev-col.us.auth0.com`)

Cualquier falla lanza `AuthenticationFailed` con el error específico.

### `config/settings/base.py` — Configuración global

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.users.auth0_backend.Auth0JWTAuthentication",
    ],
    ...
}
```

Al ser la clase de autenticación por defecto, **los 20+ endpoints existentes** (cuentas, transacciones, categorías) quedaron protegidos con Auth0 sin modificar ninguno de ellos.

---

## Ciclo de vida del token

| Momento | Frontend | Backend |
|---|---|---|
| Login exitoso | Guarda `access_token` + `refresh_token` en localStorage | — |
| Cada request | `getAccessTokenSilently()` retorna el token vigente | Valida firma, audience, issuer |
| Token expirado (1h) | SDK hace refresh silencioso con `refresh_token` | Rechaza con 401 si llega expirado |
| Primer request de usuario nuevo | Envía el token | Crea usuario en BD + llama /userinfo |
| Logout | Borra localStorage + invalida sesión en Auth0 | — |

---

## Por qué este diseño

| Decisión | Alternativa | Razón |
|---|---|---|
| Auth0 en vez de auth propio | SimpleJWT + registro propio | Seguridad gestionada por especialistas; soporte para Google sin código |
| PKCE en el frontend | `client_secret` | Las SPAs no pueden guardar secretos de forma segura |
| Validar JWT localmente en el backend | Llamar a Auth0 en cada request | Sin dependencia de red para validar; mucho más rápido |
| `auth0_sub` en la BD | Solo usar Auth0 como fuente de verdad | Django necesita FKs reales para cuentas, transacciones, etc. |
| Llamar a `/userinfo` solo cuando faltan datos | Siempre o nunca | Balance entre frescura de datos y latencia |
| RS256 (asimétrico) | HS256 (secreto compartido) | El secreto nunca sale de Auth0; la clave pública es suficiente para verificar |
| `cacheLocation="localstorage"` | Cookies (sessionStorage) | Permite refresh silencioso sin cookies de terceros, bloqueadas en navegadores modernos |

---

## Conceptos clave

- **JWT:** token firmado que contiene claims (sub, email, exp, aud). No requiere consultar una BD para validarlo — la firma lo garantiza.
- **RS256:** algoritmo asimétrico. Auth0 firma con clave privada (solo Auth0 la tiene); cualquiera puede verificar con la clave pública (JWKS). Nadie puede falsificar un token sin la clave privada.
- **JWKS:** endpoint público donde Auth0 expone sus claves públicas en formato estándar.
- **`sub`:** identificador único e inmutable del usuario en Auth0. Es la fuente de verdad para la identidad, independiente del email (que puede cambiar).
- **Access Token vs ID Token:** el Access Token autoriza llamadas a la API (lo usa el backend); el ID Token describe al usuario para el frontend. Son tokens distintos con propósitos distintos.
- **`getAccessTokenSilently()`:** función del SDK que retorna el token vigente, renovándolo automáticamente si expiró. El desarrollador nunca maneja el refresh manualmente.
- **`get_or_create`:** operación atómica de Django — busca por un campo único y crea si no existe, en una sola query sin race conditions.
- **`isLoading`:** estado de Auth0 que indica que el SDK está restaurando la sesión. Ignorarlo causaría que usuarios autenticados sean redirigidos al login en cada recarga.
