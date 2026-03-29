# Plutus Backend

API REST para la gestión de finanzas personales, construida con Django 6 y Django REST Framework.

## Requisitos previos

- Python 3.12+
- Docker y Docker Compose (para la base de datos PostgreSQL)

## Instalación

### 1. Levantar la base de datos

```bash
docker compose up -d
```

Esto inicia un contenedor de PostgreSQL 16 en el puerto `3434`.

### 2. Crear el entorno virtual e instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` según sea necesario. Los valores por defecto funcionan para desarrollo local con la base de datos de Docker.

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. (Opcional) Crear un superusuario

```bash
python manage.py createsuperuser
```

### 6. Iniciar el servidor

```bash
python manage.py runserver
```

La API estará disponible en `http://localhost:8000/api/`.

## Documentación de la API

La documentación interactiva (Swagger UI) se encuentra en:

```
http://localhost:8000/api/docs/
```

## Comandos útiles

| Comando | Descripción |
|---|---|
| `docker compose up -d` | Inicia la base de datos |
| `docker compose down` | Detiene la base de datos |
| `python manage.py runserver` | Inicia el servidor de desarrollo |
| `python manage.py migrate` | Aplica migraciones pendientes |
| `python manage.py makemigrations` | Genera migraciones tras cambios en modelos |
| `python manage.py createsuperuser` | Crea un usuario administrador |

## Estructura del proyecto

```
apps/
├── accounts/       # Cuentas bancarias y financieras
├── categories/     # Categorías de transacciones
├── transactions/   # Ingresos, gastos y transferencias
├── users/          # Autenticación y perfil de usuario (Auth0)
├── loans/          # (pendiente)
├── reports/        # (pendiente)
└── subscriptions/  # (pendiente)
common/             # Mixins, permisos y paginación compartidos
config/             # Configuración de Django (settings, urls, wsgi)
```

## Tecnologías principales

- Django 6.0 / Django REST Framework 3.17
- PostgreSQL 16 (vía Docker)
- Auth0 (autenticación JWT con RS256)
- drf-spectacular (documentación OpenAPI)
- django-filter (filtros avanzados)
