# Plan: Plutus Backend — API de Finanzas Personales con Django

## TL;DR

Backend API REST con Django + DRF para gestión de finanzas personales. Arquitectura convencional Django con **Service Layer** para separar lógica de negocio. Patrones de diseño esenciales: **Strategy**, **Observer (Signals)** y **Factory Method**. PostgreSQL + Docker + JWT auth. Frontend será React/Next.js.

---

## Fase 0: Setup del Proyecto

1. Crear proyecto Django con estructura modular (`config/` para settings, `apps/` para las apps)
2. Configurar settings divididos en `base.py`, `dev.py`, `prod.py` (12-factor app con `django-environ`)
3. Docker + Docker Compose: container para Django + PostgreSQL 16
4. Dependencias: `django`, `djangorestframework`, `simplejwt`, `django-cors-headers`, `django-filter`, `psycopg`, `django-environ`, `drf-spectacular`
5. Modelo de usuario custom extendiendo `AbstractUser` ANTES de la primera migración

### Estructura de carpetas

```
plutus-backend/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements/
│   ├── base.txt
│   └── dev.txt
├── manage.py
├── config/                     # Proyecto Django (settings, urls, wsgi)
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/                  # Auth + User management
│   ├── accounts/               # Cuentas bancarias, wallets, tarjetas
│   ├── categories/             # Categorías de transacciones
│   ├── transactions/           # Ingresos, gastos, transferencias
│   ├── subscriptions/          # Pagos recurrentes
│   ├── loans/                  # Préstamos y deudas
│   └── reports/                # Estadísticas y reportes
└── common/                     # Utilidades compartidas
    ├── mixins.py
    ├── permissions.py
    └── pagination.py
```

Cada app sigue:

```
app_name/
├── models.py          # Modelos Django ORM
├── serializers.py     # Serializers DRF
├── services.py        # ⭐ Service Layer
├── views.py           # ViewSets (thin)
├── urls.py
├── signals.py         # Observer pattern
└── strategies.py      # Strategy pattern (donde aplique)
```

---

## Fase 1: Users & Auth (JWT)

5. Modelo `User` extendiendo `AbstractUser` + `currency_default`
6. Endpoints: register, login (JWT), refresh, me (GET/PATCH)
7. Permiso custom `IsOwner`

## Fase 2: Accounts (paralela con Fase 3)

8. Modelo `Account`: name, account_type (BANK/WALLET/CREDIT_CARD/CASH), currency, balance, color, icon. Tarjetas: credit_limit, interest_rate, cut_off_day, payment_day. Soft delete.
9. CRUD ViewSet filtrado por usuario
10. `AccountService`: get_total_balance(), get_available_credit()

## Fase 3: Categories (paralela con Fase 2)

11. Modelo `Category`: name, type (INCOME/EXPENSE), icon, color, is_default, user FK nullable
12. Data migration con categorías por defecto
13. CRUD ViewSet

## Fase 4: Transactions (depende de 2 y 3) — Strategy + Observer + Factory Method

14. Modelo `Transaction`: amount, type (INCOME/EXPENSE/TRANSFER), date, description, FK Account/Category/User, destination_account nullable
15. **Strategy Pattern**: TransactionStrategy interface → IncomeStrategy, ExpenseStrategy, TransferStrategy
16. **Observer (Signals)**: post_save/post_delete → actualizar balance
17. **Factory Method**: TransactionService selecciona strategy según tipo
18. Filtros con django-filter

## Fase 5: Subscriptions (depende de 4)

19. Modelo `Subscription`: name, amount, frequency, start_date, next_payment_date, FK Account/Category/User
20. `SubscriptionService.process_due_subscriptions()` via management command
21. CRUD ViewSet + pause/resume

## Fase 6: Loans & Debt (independiente de 4-5) — Strategy Pattern

22. Modelo `Loan`: total_amount, interest_rate, type (LENT/BORROWED), person_name, status
23. Modelo `LoanPayment`: amount, date, notes, FK Loan
24. **Strategy Pattern**: SimpleInterestStrategy, CompoundInterestStrategy, NoInterestStrategy
25. `LoanService`: calculate_total_owed(), register_payment(), get_debt_summary()

## Fase 7: Reports (depende de todo)

26. `ReportService`: income vs expenses, by category, balance history, financial summary
27. Endpoints read-only en /api/reports/

## Fase 8: Docker (paralela desde Fase 0)

28. Dockerfile multi-stage Python 3.12
29. docker-compose.yml: web + db
30. .env.example, CORS, drf-spectacular en /api/docs/

---

## Patrones de Diseño (Refactoring Guru)

| Patrón          | Dónde                                           | Para qué                              |
| --------------- | ----------------------------------------------- | ------------------------------------- |
| Service Layer   | Todas las apps                                  | Separar lógica de negocio             |
| Strategy        | transactions/strategies.py, loans/strategies.py | Algoritmos intercambiables            |
| Observer        | transactions/signals.py                         | Actualizar balance automáticamente    |
| Factory Method  | TransactionService                              | Seleccionar strategy correcta         |
| Template Method | common/mixins.py                                | ViewSet base con filtrado por usuario |

## Orden de dependencias

```
Fase 0 → Fase 1 → Fases 2,3,6,8 (paralelas) → Fase 4 → Fase 5 → Fase 7
```

## Decisiones

- No tests por ahora (pytest-django después)
- No Celery — suscripciones via management command
- Soft delete en cuentas
- Categorías sistema + custom por usuario
