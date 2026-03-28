# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment

The database runs in Docker (PostgreSQL 16, port 3434). The Django API runs locally in a virtualenv.

```bash
# Start the database
docker compose up -d

# First-time setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt

# Run migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Start the API
python manage.py runserver

# Other common commands
python manage.py createsuperuser
python manage.py shell
```

No test suite exists yet (pytest-django is planned but not configured).

Dependencies are split into `requirements/base.txt` (prod) and `requirements/dev.txt` (imports base + dev-only packages).

## Settings

Settings are split into three files under `config/settings/`:
- `base.py` — shared across all environments
- `dev.py` — imports `base.*` and overrides for local development (DEBUG=True, CORS_ALLOW_ALL_ORIGINS=True)
- `prod.py` — imports `base.*` with HTTPS enforcement and strict ALLOWED_HOSTS

The active settings module is controlled via `DJANGO_SETTINGS_MODULE` in `.env`. Dev uses `config.settings.dev`.

A `.env` file at the project root is required. Required variables: `SECRET_KEY`, `DATABASE_URL`, `DEBUG`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`.

## API

- Base URL: `http://localhost:8000/api/`
- Auth: Auth0 JWT Bearer tokens (RS256). The frontend obtains tokens from Auth0; Django validates them via JWKS (`apps/users/auth0_backend.py`). On first login, the backend auto-creates a Django user from the `sub` claim and fetches the profile from Auth0's `/userinfo`. Only `GET/PATCH /api/auth/me/` exists on the backend — login and token refresh are handled entirely by Auth0.
- Swagger UI: `http://localhost:8000/api/docs/`
- All endpoints require `IsAuthenticated` by default (set globally in `REST_FRAMEWORK`).
- Pagination: 20 items/page. Override with `?page_size=N` (max 100).
- Filtering: `django-filter` + `SearchFilter` + `OrderingFilter` enabled globally.

## Architecture

### Service Layer
Business logic lives exclusively in `services.py` per app. Views are thin — they validate input via serializers and delegate to the service. Never put business logic in views or models.

### Design Patterns

**Strategy + Factory Method (`transactions/strategies.py`, `transactions/services.py`)**
`TransactionStrategy` is an ABC with `apply()` and `revert()`. Concrete strategies: `IncomeStrategy`, `ExpenseStrategy`, `TransferStrategy`. `TransactionService._strategies` is the factory dict mapping `TransactionType` → strategy instance. Adding a new transaction type means creating a new strategy class and registering it there — no other code changes needed.

**Observer via Django Signals (`transactions/signals.py`)**
`post_save` and `post_delete` on `Transaction` automatically call `strategy.apply()` / `strategy.revert()` to update account balances. Signals are registered in `TransactionsConfig.ready()` (`apps/transactions/apps.py`). Only `created=True` saves trigger `apply()`; editing a transaction does **not** rebalance (known limitation, marked as TODO).

**Template Method via `OwnerFilterMixin` (`common/mixins.py`)**
All ViewSets that show user-owned data inherit `OwnerFilterMixin` as the first base class (MRO matters). It overrides `get_queryset()` to filter by `request.user` and `perform_create()` to inject `user=request.user`. The field name defaults to `"user"` and can be overridden via `owner_field`.

### Shared Utilities (`common/`)

- **`common/mixins.py`** — `OwnerFilterMixin` (see above).
- **`common/permissions.py`** — `IsOwner` DRF permission that checks `obj.user == request.user`. Use for object-level access control where `OwnerFilterMixin` isn't enough.
- **`common/pagination.py`** — `StandardPagination` (20/page, max 100). Already registered globally; don't set pagination per-ViewSet unless you need a different page size.

### Data Model Conventions
- `amount` on `Transaction` is always positive; the strategy determines whether it adds or subtracts from `balance`.
- `Account` uses soft delete: `is_active=False` instead of DB deletion, so transaction history is preserved. `AccountService.soft_delete()` handles this; `destroy()` in `AccountViewSet` is overridden accordingly.
- `Category.user = NULL` means a system-wide default category; a non-null FK means it's user-created. Default categories are seeded via migration `0002_seed_default_categories`.
- Credit card fields (`credit_limit`, `interest_rate`, `cut_off_day`, `payment_day`) are nullable on `Account` and only apply when `account_type=CREDIT_CARD`.
- Always use `DecimalField` for monetary values, never `FloatField`.
- `TransactionViewSet` uses `select_related("account", "destination_account", "category")` — follow this pattern in other ViewSets to avoid N+1 queries.

### Incomplete Apps
`apps/loans/` and `apps/reports/` directories exist but are empty — they are not yet in `INSTALLED_APPS`. `apps/subscriptions/` also exists but has no implementation files. When implementing these, follow the same structure as `accounts` or `transactions`.

### Adding a New App
1. Create files under `apps/<name>/`: `models.py`, `serializers.py`, `services.py`, `views.py`, `urls.py`, `apps.py`, `migrations/__init__.py`
2. Add `"apps.<name>"` to `LOCAL_APPS` in `config/settings/base.py`
3. Register URLs in `config/urls.py`
4. If the app has signals, import them in `AppConfig.ready()`
