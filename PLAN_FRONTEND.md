# Plan: Plutus Frontend — App de Finanzas Personales

## TL;DR

SPA minimalista con **Vite + React + TypeScript** para gestión de finanzas personales. UI con **shadcn/ui** (instalado via MCP), dark mode por defecto, estado global con **Zustand**. Se conecta a la API REST de Plutus Backend (Django + DRF). Repo independiente (`plutus-frontend`).

---

## Decisiones de Arquitectura

| Decisión      | Elección                         | Razón                                                                           |
| ------------- | -------------------------------- | ------------------------------------------------------------------------------- |
| Framework     | **Vite + React Router**          | App privada (tú y amigos), no necesita SSR/SEO. Más simple y rápido que Next.js |
| Lenguaje      | **TypeScript**                   | Tipado de los responses de la API, autocompletado, menos bugs                   |
| UI            | **shadcn/ui** (via MCP)          | Componentes copiados al proyecto, full control, minimalista por naturaleza      |
| Estado global | **Zustand**                      | Minimal boilerplate, perfecto para auth state y caches simples                  |
| Server state  | **TanStack Query (React Query)** | Cache, refetch, loading/error states automáticos para la API                    |
| HTTP client   | **Axios**                        | Interceptors para JWT (auto-refresh, auto-attach token)                         |
| Routing       | **React Router v7**              | File-based routing no necesario, routes explícitas más simples                  |
| Formularios   | **React Hook Form + Zod**        | Validación tipada, integración nativa con shadcn/ui                             |
| Tema          | **Dark mode por defecto**        | Minimalista + dark = moderno. Toggle disponible                                 |
| Idioma        | **Español**                      | UI en español, sin i18n por ahora                                               |
| Repo          | **Separado** (`plutus-frontend`) | Deploy independiente, CI/CD independiente, concerns separados                   |

---

## Estructura del Proyecto

```
plutus-frontend/
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── components.json              ← Config de shadcn/ui
├── tsconfig.json
├── .env                         ← VITE_API_URL=http://localhost:8000/api
│
├── src/
│   ├── main.tsx                 ← Entry point + providers
│   ├── App.tsx                  ← Router setup
│   │
│   ├── api/                     ← Capa HTTP
│   │   ├── client.ts            ← Axios instance + interceptors JWT
│   │   ├── auth.ts              ← login(), register(), refreshToken()
│   │   ├── accounts.ts          ← getAccounts(), createAccount(), etc.
│   │   ├── categories.ts        ← getCategories(), createCategory()
│   │   └── transactions.ts      ← getTransactions(), createTransaction(), getSummary()
│   │
│   ├── hooks/                   ← Custom hooks (TanStack Query wrappers)
│   │   ├── use-auth.ts          ← useLogin(), useRegister(), useUser()
│   │   ├── use-accounts.ts      ← useAccounts(), useCreateAccount(), useSummary()
│   │   ├── use-categories.ts    ← useCategories(), useCreateCategory()
│   │   └── use-transactions.ts  ← useTransactions(), useCreateTransaction()
│   │
│   ├── stores/                  ← Zustand stores
│   │   └── auth-store.ts        ← tokens, user, isAuthenticated, login/logout actions
│   │
│   ├── components/
│   │   ├── ui/                  ← shadcn/ui (auto-generados via MCP)
│   │   ├── layout/              ← Shell de la app
│   │   │   ├── sidebar.tsx
│   │   │   ├── header.tsx
│   │   │   └── app-layout.tsx
│   │   ├── accounts/
│   │   │   ├── account-card.tsx
│   │   │   ├── account-form.tsx
│   │   │   └── account-list.tsx
│   │   ├── transactions/
│   │   │   ├── transaction-form.tsx
│   │   │   ├── transaction-list.tsx
│   │   │   └── transaction-filters.tsx
│   │   ├── categories/
│   │   │   ├── category-badge.tsx
│   │   │   └── category-form.tsx
│   │   └── dashboard/
│   │       ├── balance-card.tsx
│   │       ├── recent-transactions.tsx
│   │       └── summary-chart.tsx
│   │
│   ├── pages/                   ← Páginas (1 por ruta)
│   │   ├── auth/
│   │   │   ├── login.tsx
│   │   │   └── register.tsx
│   │   ├── dashboard.tsx
│   │   ├── accounts.tsx
│   │   ├── transactions.tsx
│   │   └── categories.tsx
│   │
│   ├── lib/
│   │   ├── utils.ts             ← cn() helper, formatCurrency()
│   │   └── validators.ts        ← Schemas Zod compartidos
│   │
│   └── types/
│       ├── auth.ts
│       ├── account.ts
│       ├── category.ts
│       └── transaction.ts
│
└── public/
    └── favicon.svg
```

---

## Pantallas MVP

### 1. Auth — Login / Register

- Formulario centrado, fondo oscuro, logo arriba
- React Hook Form + Zod
- Al login exitoso → tokens en Zustand → redirect a Dashboard
- Auto-refresh vía interceptor Axios

### 2. Dashboard — Resumen Financiero

- Summary cards: ingresos, gastos, neto (GET /transactions/summary/)
- Lista de cuentas con balance (GET /accounts/summary/)
- Últimas 5 transacciones (GET /transactions/?ordering=-date)
- Sidebar colapsable en mobile

### 3. Cuentas — CRUD

- Cards con nombre, tipo, balance, ícono, color
- Dialog crear/editar con campos condicionales (crédito)
- Soft delete con confirmación

### 4. Transacciones — Lista + Crear

- DataTable con paginación server-side
- Filtros: tipo, cuenta, categoría, rango fechas
- Dialog crear: tabs por tipo, categorías filtradas, date picker

### 5. Categorías — Gestión

- Tabs Gastos | Ingresos
- Badge "Sistema" para is_default (no editable)
- Dialog crear custom con color picker

---

## Fases de Implementación

### Fase F0: Scaffolding _(sin dependencias)_

1. Crear repo `plutus-frontend`, init Vite + React + TS
2. Instalar y configurar Tailwind CSS v4
3. Configurar shadcn/ui via MCP
4. Dark mode por defecto (class strategy)
5. Path aliases (`@/` → `src/`)
6. `.env` con `VITE_API_URL`

**Verificación:** `npm run dev` → localhost:5173, dark mode visible

### Fase F1: Auth + HTTP Layer _(depende de F0)_

7. Axios instance + interceptors JWT (attach token, auto-refresh on 401)
8. Zustand auth-store: tokens, user, isAuthenticated, login(), logout()
9. Páginas Login y Register (RHF + Zod)
10. ProtectedRoute component
11. Router: /login, /register (públicas) + / (protegidas)

**Verificación:** Login con santiago/test1234seguro → redirect a dashboard

### Fase F2: Layout + Dashboard _(depende de F1)_

12. AppLayout: sidebar + header + content
13. Sidebar minimalista: íconos + labels, colapsable
14. Header: título, avatar/menú, theme toggle
15. Dashboard: summary cards, cuentas, últimas transacciones

**Verificación:** Dashboard muestra datos reales del backend

### Fase F3: Cuentas CRUD _(paralela con F4)_

16. Lista de account cards
17. Dialog crear/editar (campos condicionales tarjetas)
18. Soft delete con confirmación
19. Resumen balance total por moneda

**Verificación:** Crear cuenta → aparece en lista → editar → soft delete

### Fase F4: Transacciones _(paralela con F3)_

20. DataTable con paginación server-side
21. Filtros: tipo, cuenta, categoría, fechas
22. Dialog crear: tabs tipo, categorías filtradas, account selector
23. Eliminar con confirmación

**Verificación:** Crear ingreso → balance de cuenta sube automáticamente

### Fase F5: Categorías _(depende de F1)_

24. Tabs Gastos | Ingresos
25. Badge "Sistema" (no editable)
26. Dialog crear custom con color picker
27. Editar/eliminar solo propias

**Verificación:** Crear categoría custom → aparece al crear transacción

---

## Dependencias npm

```
# Core
react react-dom react-router

# Build
vite @vitejs/plugin-react typescript

# UI
tailwindcss @tailwindcss/vite
# shadcn/ui via MCP (no es npm package)

# Estado + Data
zustand @tanstack/react-query axios

# Formularios
react-hook-form @hookform/resolvers zod

# Utilidades
lucide-react date-fns clsx tailwind-merge
```

---

## Componentes shadcn/ui Necesarios

| Componente         | Uso                          |
| ------------------ | ---------------------------- |
| button             | CTAs, submit                 |
| card               | Dashboard, account cards     |
| input, label       | Formularios                  |
| select             | Selectors                    |
| dialog             | Modals crear/editar          |
| sheet              | Sidebar mobile               |
| table              | Lista transacciones          |
| tabs               | Tipo transacción, categorías |
| badge              | Tipo, sistema                |
| avatar             | User menu                    |
| dropdown-menu      | Acciones                     |
| separator          | Divisores                    |
| skeleton           | Loading states               |
| sonner             | Notificaciones               |
| form               | RHF wrapper                  |
| popover + calendar | Date picker                  |
| command            | Combobox categorías/cuentas  |

---

## Mapeo API → Frontend

| Endpoint                   | Hook                   | Página                   |
| -------------------------- | ---------------------- | ------------------------ |
| POST /auth/login/          | useLogin()             | Login                    |
| POST /auth/register/       | useRegister()          | Register                 |
| POST /auth/refresh/        | Axios interceptor      | (auto)                   |
| GET /auth/me/              | useUser()              | Header, Dashboard        |
| GET /accounts/             | useAccounts()          | Cuentas, Dashboard       |
| POST /accounts/            | useCreateAccount()     | Cuentas                  |
| PATCH /accounts/{id}/      | useUpdateAccount()     | Cuentas                  |
| DELETE /accounts/{id}/     | useDeleteAccount()     | Cuentas                  |
| GET /accounts/summary/     | useAccountSummary()    | Dashboard                |
| GET /categories/           | useCategories()        | Categorías, TX Form      |
| POST /categories/          | useCreateCategory()    | Categorías               |
| GET /transactions/         | useTransactions()      | Transacciones, Dashboard |
| POST /transactions/        | useCreateTransaction() | Transacciones            |
| DELETE /transactions/{id}/ | useDeleteTransaction() | Transacciones            |
| GET /transactions/summary/ | useTxSummary()         | Dashboard                |

---

## Orden de Dependencias

```
F0 (Setup) → F1 (Auth) → F2 (Layout + Dashboard) → F3 & F4 (paralelas) → F5 (Categorías)
```

## Alcance

**Incluido:** Auth, Dashboard, CRUD cuentas, transacciones, categorías, dark mode, responsive
**Excluido (futuro):** Charts (Recharts), PWA, suscripciones, préstamos, export, i18n
