# Plutus Frontend — Plan de Implementación para IA

> Instrucciones ejecutables paso a paso para construir el frontend de Plutus.
> **Mobile-first**: la app se usará principalmente en smartphones.

---

## 0. REGLAS GLOBALES

Estas reglas aplican a TODAS las fases. Léelas antes de escribir cualquier código.

1. **Mobile-first**: diseñar para 360px primero, escalar a tablet/desktop con breakpoints Tailwind (`sm:`, `md:`, `lg:`).
2. **Touch targets**: mínimo `h-11` (44px) para botones y elementos interactivos.
3. **Nunca enviar `user` o `user_id`** en requests. El backend lo infiere del JWT.
4. **Decimals**: el backend envía montos como strings (`"3000000.00"`). Parsear con `parseFloat()` solo para mostrar. Enviar siempre como string.
5. **Trailing slash**: todas las URLs de la API terminan en `/` (`/accounts/`, no `/accounts`). Configurar `baseURL` en Axios SIN trailing slash.
6. **Error format del backend**: `{ "field_name": ["error message"] }` o `{ "detail": "message" }`. Manejar ambos.
7. **Invalidación de queries**: al crear/editar/eliminar → invalidar queries relacionadas. Crear transacción invalida `["transactions"]` Y `["accounts"]` (balance cambia).
8. **Loading states**: usar `Skeleton` de shadcn para todos los datos que cargan.
9. **Toasts**: usar sonner. Éxito en verde, error en rojo. Mostrar mensaje del backend.
10. **DRY**: Los hooks de TanStack Query son la única interfaz entre componentes y la API. Los componentes nunca llaman a Axios directamente.
11. **Shadcn via MCP**: instalar componentes con la herramienta MCP de shadcn, no manualmente.
12. **Idioma**: toda la UI en español.

---

## 1. CONTEXTO

- **Backend**: Django REST API en `http://localhost:8000/api`
- **Auth**: JWT — access 30min, refresh 7 días, rotation activada
- **Paginación**: `{ count, next, previous, results }`, page_size=20, max=100
- **Permisos**: todos los endpoints (excepto login/register) requieren `Authorization: Bearer <token>`
- **Repo destino**: `/home/santiagomg/Documents/Development/plutus/plutus-frontend`
- **SSH Git**: `git@github.com-personal:SantiagoMGS/plutus-frontend.git`

---

## 2. DESIGN SYSTEM

### Stack visual

- **shadcn/ui** estilo `new-york`, base `zinc`, CSS variables activas
- **Tailwind CSS v4** con `@tailwindcss/vite`
- **Dark mode por defecto** (`class="dark"` en `<html>`) + toggle light/dark en header

### Breakpoints (Tailwind defaults, mobile-first)

| Nombre | Min-width | Uso |
|--------|-----------|-----|
| (base) | 0px | Smartphones (360–639px). Layout por defecto. |
| `sm` | 640px | Smartphones grandes / landscape |
| `md` | 768px | Tablets. Sidebar visible, grids 2 cols. |
| `lg` | 1024px | Desktop. Grids 3 cols. |

### Colores semánticos (clases Tailwind)

| Concepto | Texto | Fondo | Uso |
|----------|-------|-------|-----|
| Income | `text-emerald-500` | `bg-emerald-500/10` | Ingresos, montos positivos |
| Expense | `text-red-500` | `bg-red-500/10` | Gastos, montos negativos |
| Transfer | `text-blue-500` | `bg-blue-500/10` | Transferencias |
| Primary | `text-primary` | `bg-primary` | Botones principales, links activos |
| Muted | `text-muted-foreground` | `bg-muted` | Texto secundario, fondos sutiles |
| Card | — | `bg-card` | Fondo de cards |
| Destructive | `text-destructive` | `bg-destructive` | Errores, eliminar |

### Tipografía

- Font: la de shadcn por defecto (Inter via CSS variables)
- Títulos de página: `text-xl font-semibold` en mobile, `md:text-2xl`
- Subtítulos / labels: `text-sm text-muted-foreground`
- Montos grandes (dashboard): `text-2xl font-bold tabular-nums`
- Montos en listas: `text-sm font-medium tabular-nums`

### Espaciado

- Padding de página: `px-4 py-4` en mobile, `md:px-6 md:py-6`
- Gap entre cards: `gap-4`
- Padding interno de cards: `p-4` en mobile, `md:p-6`

### Layout principal

- **Mobile (< md)**: Bottom navigation bar fija + header simple arriba
- **Desktop (≥ md)**: Sidebar izquierda 240px + header sticky
- Content: `max-w-5xl mx-auto` en desktop, full-width en mobile

### Navegación bottom bar (mobile < md)

```
Contenedor: fixed bottom-0 inset-x-0 h-16 border-t bg-background/95 backdrop-blur z-50
             flex items-center justify-around px-2
             md:hidden
```

4 items, cada uno `flex flex-col items-center justify-center gap-0.5 min-w-[64px] py-2`:

| Label | Ícono lucide (size 20) | Ruta |
|-------|----------------------|------|
| Inicio | `LayoutDashboard` | `/` |
| Cuentas | `Wallet` | `/accounts` |
| Movimientos | `ArrowLeftRight` | `/transactions` |
| Categorías | `Tag` | `/categories` |

- Activo: `text-primary`
- Inactivo: `text-muted-foreground`
- Label: `text-[10px] leading-none`

### Sidebar (desktop ≥ md)

```
Contenedor: hidden md:flex flex-col w-60 h-screen border-r bg-card fixed left-0 top-0
```

- Header: "Plutus" `text-lg font-bold p-4`
- Mismos 4 nav items que el bottom-nav, con label `text-sm` al lado del ícono
- Cada item: `flex items-center gap-3 px-3 h-10 rounded-md`
- Activo: `bg-muted text-primary`
- Inactivo: `text-muted-foreground hover:bg-muted/50`
- Footer: botón logout `text-sm text-muted-foreground`

### Header

```
Contenedor: sticky top-0 z-40 h-14 border-b bg-background/95 backdrop-blur
             flex items-center justify-between px-4
             md:pl-64
```

- Izquierda: título de página actual `text-lg font-semibold`
- Derecha: botón theme toggle (Sun/Moon, `h-9 w-9`) + avatar dropdown (perfil, cerrar sesión)

### Dialogs / Forms en mobile

- En mobile (< md): usar `Sheet` de shadcn como drawer bottom (`side="bottom"`) en vez de Dialog centrado.
- En desktop (≥ md): usar `Dialog` centrado normal.
- Esto aplica a: AccountForm, TransactionForm, CategoryForm, TransactionFilters.

---

## 3. ESTRUCTURA DE ARCHIVOS

```
plutus-frontend/
├── index.html
├── vite.config.ts
├── components.json                      ← Config de shadcn/ui
├── tsconfig.json
├── .env                                 ← VITE_API_URL=http://localhost:8000/api
├── public/
│   └── favicon.svg
└── src/
    ├── main.tsx                         ← Entry + Providers
    ├── App.tsx                          ← Router setup
    ├── index.css                        ← Tailwind + shadcn theme
    │
    ├── types/
    │   ├── api.ts                       ← PaginatedResponse<T>
    │   ├── auth.ts                      ← User, LoginRequest, LoginResponse, etc.
    │   ├── account.ts                   ← Account, AccountCreateRequest, AccountSummary
    │   ├── category.ts                  ← Category, CategoryCreateRequest
    │   └── transaction.ts               ← Transaction, TransactionCreateRequest, TransactionSummary
    │
    ├── api/
    │   ├── client.ts                    ← Axios instance + interceptors JWT
    │   ├── auth.ts                      ← login(), register(), getMe(), changePassword()
    │   ├── accounts.ts                  ← getAccounts(), createAccount(), updateAccount(), deleteAccount(), getSummary()
    │   ├── categories.ts                ← getCategories(), createCategory(), updateCategory(), deleteCategory()
    │   └── transactions.ts              ← getTransactions(), createTransaction(), deleteTransaction(), getSummary()
    │
    ├── hooks/
    │   ├── use-auth.ts                  ← useLogin(), useRegister(), useUser()
    │   ├── use-accounts.ts              ← useAccounts(), useCreateAccount(), useUpdateAccount(), useDeleteAccount(), useAccountSummary()
    │   ├── use-categories.ts            ← useCategories(), useCreateCategory(), useUpdateCategory(), useDeleteCategory()
    │   └── use-transactions.ts          ← useTransactions(), useCreateTransaction(), useDeleteTransaction(), useTxSummary()
    │
    ├── stores/
    │   └── auth-store.ts                ← Zustand: tokens, user, isAuthenticated, setTokens, setUser, logout
    │
    ├── lib/
    │   ├── utils.ts                     ← cn(), formatCurrency()
    │   └── validators.ts                ← Schemas Zod: loginSchema, registerSchema, accountSchema, transactionSchema, categorySchema
    │
    ├── components/
    │   ├── ui/                          ← shadcn/ui (auto-generados via MCP)
    │   ├── protected-route.tsx
    │   ├── layout/
    │   │   ├── app-layout.tsx           ← Shell: header + sidebar/bottomnav + content
    │   │   ├── sidebar.tsx              ← Desktop only (hidden en < md)
    │   │   ├── bottom-nav.tsx           ← Mobile only (hidden en ≥ md)
    │   │   └── header.tsx               ← Sticky top: título + theme toggle + avatar
    │   ├── dashboard/
    │   │   ├── balance-card.tsx
    │   │   └── recent-transactions.tsx
    │   ├── accounts/
    │   │   ├── account-card.tsx
    │   │   └── account-form.tsx
    │   ├── transactions/
    │   │   ├── transaction-filters.tsx
    │   │   ├── transaction-form.tsx
    │   │   └── transaction-list.tsx
    │   └── categories/
    │       ├── category-badge.tsx
    │       └── category-form.tsx
    │
    └── pages/
        ├── auth/
        │   ├── login.tsx
        │   └── register.tsx
        ├── dashboard.tsx
        ├── accounts.tsx
        ├── transactions.tsx
        └── categories.tsx
```

---

## 4. TIPOS TYPESCRIPT

Mapeados 1:1 de los serializers Django. Crear tal cual.

```typescript
// ─── src/types/api.ts ───
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ─── src/types/auth.ts ───
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  currency_default: string; // "COP" | "USD" | "EUR"
  date_joined: string;      // ISO datetime
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  currency_default?: string;
}

export interface RefreshRequest {
  refresh: string;
}

export interface RefreshResponse {
  access: string;
  refresh: string; // rotation activada, devuelve nuevo refresh
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

// ─── src/types/account.ts ───
export type AccountType = "BANK" | "WALLET" | "CREDIT_CARD" | "CASH";
export type Currency = "COP" | "USD" | "EUR";

export interface Account {
  id: number;
  name: string;
  account_type: AccountType;
  account_type_display: string; // "Cuenta Bancaria", "Billetera Digital", "Tarjeta de Crédito", "Efectivo"
  currency: Currency;
  balance: string;              // Decimal como string desde DRF
  color: string;                // hex "#4F46E5"
  icon: string;                 // "wallet", "bank", etc.
  credit_limit: string | null;
  interest_rate: string | null;
  cut_off_day: number | null;
  payment_day: number | null;
  available_credit: number | null; // calculado: credit_limit - abs(balance)
  is_active: boolean;
  created_at: string;           // ISO datetime
  updated_at: string;           // ISO datetime
}

export interface AccountCreateRequest {
  name: string;
  account_type: AccountType;
  currency?: Currency;          // default: COP
  color?: string;
  icon?: string;
  credit_limit?: string;        // obligatorio si account_type === "CREDIT_CARD"
  interest_rate?: string;
  cut_off_day?: number;
  payment_day?: number;
}

export interface AccountSummary {
  balances_by_currency: Record<string, number>; // { "COP": 2500000, "USD": 0 }
  available_credit: number;
}

// ─── src/types/category.ts ───
export type CategoryType = "INCOME" | "EXPENSE";

export interface Category {
  id: number;
  name: string;
  category_type: CategoryType;
  category_type_display: string; // "Ingreso" | "Gasto"
  icon: string;
  color: string;
  is_default: boolean;           // true = categoría del sistema (no editable)
}

export interface CategoryCreateRequest {
  name: string;
  category_type: CategoryType;
  icon?: string;
  color?: string;
}

// ─── src/types/transaction.ts ───
export type TransactionType = "INCOME" | "EXPENSE" | "TRANSFER";

export interface Transaction {
  id: number;
  transaction_type: TransactionType;
  transaction_type_display: string; // "Ingreso" | "Gasto" | "Transferencia"
  amount: string;                   // Decimal como string
  description: string;
  date: string;                     // "YYYY-MM-DD"
  account: number;
  account_name: string;
  destination_account: number | null;
  destination_account_name: string | null;
  category: number | null;
  category_name: string | null;
  created_at: string;               // ISO datetime
}

export interface TransactionCreateRequest {
  transaction_type: TransactionType;
  amount: string;
  description?: string;
  date: string;                     // "YYYY-MM-DD"
  account: number;
  destination_account?: number;     // obligatorio si type === "TRANSFER"
  category?: number;
}

export interface TransactionSummary {
  total_income: number;
  total_expenses: number;
  net: number;
  transaction_count: number;
}
```

---

## 5. ENDPOINTS

### Auth (`/api/auth/`)

| Método | URL | Auth | Body | Response | Status |
|--------|-----|------|------|----------|--------|
| POST | `/auth/login/` | No | `LoginRequest` | `LoginResponse` | 200 |
| POST | `/auth/refresh/` | No | `RefreshRequest` | `RefreshResponse` | 200 |
| POST | `/auth/register/` | No | `RegisterRequest` | `User` | 201 |
| GET | `/auth/me/` | Sí | — | `User` | 200 |
| PATCH | `/auth/me/` | Sí | `{ first_name?, last_name?, currency_default? }` | `User` | 200 |
| POST | `/auth/change-password/` | Sí | `ChangePasswordRequest` | `{}` | 200 |

### Accounts (`/api/accounts/`)

| Método | URL | Query Params | Body | Response |
|--------|-----|-------------|------|----------|
| GET | `/accounts/` | `?account_type=BANK&currency=COP&search=nequi&ordering=-balance&page=1&page_size=20` | — | `PaginatedResponse<Account>` |
| POST | `/accounts/` | — | `AccountCreateRequest` | `Account` (201) |
| GET | `/accounts/{id}/` | — | — | `Account` |
| PATCH | `/accounts/{id}/` | — | `Partial<AccountCreateRequest>` | `Account` |
| DELETE | `/accounts/{id}/` | — | — | 204 (soft delete) |
| GET | `/accounts/summary/` | — | — | `AccountSummary` |

### Categories (`/api/categories/`)

| Método | URL | Query Params | Body | Response |
|--------|-----|-------------|------|----------|
| GET | `/categories/` | `?category_type=INCOME&search=sal&ordering=name` | — | `PaginatedResponse<Category>` |
| POST | `/categories/` | — | `CategoryCreateRequest` | `Category` (201) |
| PATCH | `/categories/{id}/` | — | `Partial<CategoryCreateRequest>` | `Category` (403 si is_default) |
| DELETE | `/categories/{id}/` | — | — | 204 (403 si is_default) |

### Transactions (`/api/transactions/`)

| Método | URL | Query Params | Body | Response |
|--------|-----|-------------|------|----------|
| GET | `/transactions/` | `?transaction_type=INCOME&account=2&category=15&date=2026-03-15&search=salario&ordering=-date&page=1` | — | `PaginatedResponse<Transaction>` |
| POST | `/transactions/` | — | `TransactionCreateRequest` | `Transaction` (201) |
| GET | `/transactions/{id}/` | — | — | `Transaction` |
| DELETE | `/transactions/{id}/` | — | — | 204 (revierte balance vía signal) |
| GET | `/transactions/summary/` | `?date_from=2026-03-01&date_to=2026-03-31` | — | `TransactionSummary` |

### Validaciones backend que el frontend debe respetar

- `amount > 0` en transacciones
- `account` y `destination_account` deben pertenecer al usuario y estar activas
- `destination_account` obligatorio si `transaction_type === "TRANSFER"`
- `destination_account !== account` en transferencias
- `category.category_type` debe coincidir con `transaction_type` (INCOME→INCOME, EXPENSE→EXPENSE, TRANSFER→sin restricción)
- `credit_limit` obligatorio si `account_type === "CREDIT_CARD"`
- Categorías `is_default === true` no se editan ni borran (403)
- Categoría duplicada: mismo `name` + `category_type` del mismo usuario da 400

---

## 6. MAPEO HOOK → PÁGINA

| Endpoint | Hook | Páginas que lo usan |
|----------|------|---------------------|
| `POST /auth/login/` | `useLogin()` | Login |
| `POST /auth/register/` | `useRegister()` | Register |
| `POST /auth/refresh/` | Axios interceptor | (automático) |
| `GET /auth/me/` | `useUser()` | Header, Dashboard |
| `GET /accounts/` | `useAccounts()` | Dashboard, Cuentas, TransactionForm |
| `POST /accounts/` | `useCreateAccount()` | Cuentas |
| `PATCH /accounts/{id}/` | `useUpdateAccount()` | Cuentas |
| `DELETE /accounts/{id}/` | `useDeleteAccount()` | Cuentas |
| `GET /accounts/summary/` | `useAccountSummary()` | Dashboard, Cuentas |
| `GET /categories/` | `useCategories(type?)` | Categorías, TransactionForm |
| `POST /categories/` | `useCreateCategory()` | Categorías |
| `PATCH /categories/{id}/` | `useUpdateCategory()` | Categorías |
| `DELETE /categories/{id}/` | `useDeleteCategory()` | Categorías |
| `GET /transactions/` | `useTransactions(filters)` | Dashboard, Transacciones |
| `POST /transactions/` | `useCreateTransaction()` | Transacciones |
| `DELETE /transactions/{id}/` | `useDeleteTransaction()` | Transacciones |
| `GET /transactions/summary/` | `useTxSummary(filters?)` | Dashboard |

---

## 7. FASES DE IMPLEMENTACIÓN

### FASE F0: Scaffolding

**Objetivo**: Proyecto Vite + React + TS + Tailwind + shadcn/ui listo.

**Paso 0.1**: Crear proyecto

```bash
cd /home/santiagomg/Documents/Development/plutus
npm create vite@latest plutus-frontend -- --template react-ts
cd plutus-frontend
```

**Paso 0.2**: Instalar dependencias

```bash
npm install
npm install -D tailwindcss @tailwindcss/vite
npm install react-router zustand @tanstack/react-query axios
npm install react-hook-form @hookform/resolvers zod
npm install lucide-react date-fns clsx tailwind-merge
```

**Paso 0.3**: `vite.config.ts`

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
```

**Paso 0.4**: Reemplazar `src/index.css` con:

```css
@import "tailwindcss";
```

**Paso 0.5**: Path aliases en `tsconfig.json` y `tsconfig.app.json`, agregar en `compilerOptions`:

```json
{
  "baseUrl": ".",
  "paths": { "@/*": ["./src/*"] }
}
```

**Paso 0.6**: Inicializar shadcn/ui via MCP con: style `new-york`, base color `zinc`, CSS variables `yes`.

**Paso 0.7**: En `index.html`:

```html
<html lang="es" class="dark">
```

**Paso 0.8**: Crear `.env`:

```
VITE_API_URL=http://localhost:8000/api
```

**Paso 0.9**: Instalar componentes shadcn via MCP:

```
button card input label sonner
```

**Verificación**: `npm run dev` → localhost:5173, fondo oscuro visible.

---

### FASE F1: Auth + HTTP Layer

**Objetivo**: Login funcional, tokens en Zustand, interceptor Axios, rutas protegidas.

**Archivos a crear (en orden)**:

1. `src/types/api.ts`
2. `src/types/auth.ts`
3. `src/stores/auth-store.ts`
4. `src/api/client.ts`
5. `src/api/auth.ts`
6. `src/hooks/use-auth.ts`
7. `src/lib/validators.ts`
8. `src/pages/auth/login.tsx`
9. `src/pages/auth/register.tsx`
10. `src/components/protected-route.tsx`
11. `src/App.tsx`

**Componentes shadcn** (instalar via MCP): `form separator`

#### `src/stores/auth-store.ts`

```typescript
interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean; // derivado: accessToken !== null
  setTokens: (access: string, refresh: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
}
```

- Persistir tokens en localStorage (keys: `access_token`, `refresh_token`)
- Al inicializar, leer de localStorage
- `logout()` limpia store + localStorage

#### `src/api/client.ts` — Interceptor JWT

```
REQUEST INTERCEPTOR:
  Si hay accessToken → header Authorization: Bearer ${token}

RESPONSE ERROR 401:
  1. Si request original era /auth/login/ o /auth/refresh/ → NO reintentar
  2. Si hay refreshToken → POST /auth/refresh/ { refresh }
  3. Si refresh OK → guardar nuevos tokens, reintentar request original
  4. Si refresh falla → logout(), redirect a /login
```

#### `src/lib/validators.ts`

```typescript
// loginSchema
{
  username: z.string().min(1, "Requerido"),
  password: z.string().min(1, "Requerido"),
}

// registerSchema
{
  username: z.string().min(3, "Mínimo 3 caracteres"),
  email: z.string().email("Email inválido"),
  password: z.string().min(8, "Mínimo 8 caracteres"),
  password_confirm: z.string(),
}
.refine(data => data.password === data.password_confirm, {
  message: "Las contraseñas no coinciden",
  path: ["password_confirm"],
})
```

#### Páginas Login / Register

**Layout mobile-first**:

```
Contenedor: min-h-screen flex items-center justify-center px-4
Formulario: w-full max-w-sm space-y-6
```

- `<h1 className="text-2xl font-bold text-center">Plutus</h1>`
- `<p className="text-sm text-muted-foreground text-center">Tu dinero, bajo control</p>`
- Formulario con `<Form>` de shadcn (RHF + zodResolver)
- Todos los inputs con `h-11` (touch-friendly)
- Botón submit: `w-full h-11` con spinner + disabled durante loading
- Link entre login ↔ register: `text-sm text-primary`
- Login exitoso: `setTokens()` → `GET /auth/me/` → `setUser()` → navigate a `/`
- Errores: toast con sonner

#### Router (`src/App.tsx`)

```
/login          → LoginPage (pública)
/register       → RegisterPage (pública)
/               → Dashboard (protegida, dentro de AppLayout)
/accounts       → AccountsPage (protegida)
/transactions   → TransactionsPage (protegida)
/categories     → CategoriesPage (protegida)
```

- `ProtectedRoute`: si `!isAuthenticated` → redirect a `/login`
- Providers en `main.tsx`: `QueryClientProvider` + `BrowserRouter`
- AppLayout: placeholder `<div>` por ahora (se implementa en F2)

**Verificación**: localhost:5173 → redirige a /login → ingresar `santiago` / `test1234seguro` → redirige a / → refrescar → sigue autenticado.

---

### FASE F2: Layout + Dashboard

**Objetivo**: Shell de la app con navegación mobile-first + dashboard con datos reales.

**Archivos a crear (en orden)**:

1. `src/types/account.ts`
2. `src/types/transaction.ts`
3. `src/api/accounts.ts`
4. `src/api/transactions.ts`
5. `src/hooks/use-accounts.ts`
6. `src/hooks/use-transactions.ts`
7. `src/lib/utils.ts` — agregar `formatCurrency()`
8. `src/components/layout/bottom-nav.tsx`
9. `src/components/layout/sidebar.tsx`
10. `src/components/layout/header.tsx`
11. `src/components/layout/app-layout.tsx`
12. `src/components/dashboard/balance-card.tsx`
13. `src/components/dashboard/recent-transactions.tsx`
14. `src/pages/dashboard.tsx`

**Componentes shadcn**: `avatar dropdown-menu sheet skeleton badge separator`

#### `formatCurrency()`

```typescript
function formatCurrency(amount: string | number, currency: string = "COP"): string;
// formatCurrency("2500000", "COP") → "$2.500.000"
// formatCurrency("1500.50", "USD") → "US$1,500.50"
// Usar Intl.NumberFormat con locale "es-CO"
```

#### AppLayout

```tsx
<div className="min-h-screen bg-background">
  <Sidebar />          {/* hidden en < md, visible en md+ */}
  <Header />
  <main className="pb-20 md:pb-6 md:pl-60 px-4 py-4 md:px-6">
    <div className="max-w-5xl mx-auto">
      <Outlet />
    </div>
  </main>
  <BottomNav />        {/* visible en < md, hidden en md+ */}
</div>
```

- `pb-20` en mobile para que el contenido no quede tapado por el bottom-nav.

#### Dashboard

Tres secciones verticales con `space-y-6`:

**1. Summary cards** — `grid grid-cols-1 sm:grid-cols-3 gap-4`

Cada card: `<Card className="p-4">`
- Label: `text-sm text-muted-foreground`
- Monto: `text-2xl font-bold tabular-nums`
- Colores:
  - Ingresos: monto en `text-emerald-500`, ícono `ArrowDownLeft`
  - Gastos: monto en `text-red-500`, ícono `ArrowUpRight`
  - Balance neto: monto en `text-foreground`, ícono `TrendingUp`
- Datos: `GET /transactions/summary/` (sin filtros = todo el historial)

**2. Cuentas** — `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4`

Cada card `<Card className="p-4">`:
- Izquierda: círculo `w-10 h-10 rounded-full` con `backgroundColor: account.color` + ícono blanco
- Centro: nombre `text-sm font-medium`, tipo `text-xs text-muted-foreground`
- Derecho: balance formateado `text-sm font-bold tabular-nums`
- Datos: `GET /accounts/`

**3. Últimas transacciones** — lista vertical

- Datos: `GET /transactions/?ordering=-date&page_size=5`
- Cada item: `flex items-center justify-between py-3 border-b last:border-0`
  - Izquierda: ícono por tipo en círculo `w-9 h-9` + descripción y cuenta
  - Derecha: monto con color y signo
- INCOME → `text-emerald-500` + `ArrowDownLeft` + prefijo `+`
- EXPENSE → `text-red-500` + `ArrowUpRight` + prefijo `-`
- TRANSFER → `text-blue-500` + `ArrowLeftRight`

Loading: `Skeleton` de shadcn en cada sección.

**Verificación**: Dashboard muestra datos reales. Bottom nav funciona en mobile. Sidebar visible en desktop ≥ 768px.

---

### FASE F3: Cuentas CRUD

**Objetivo**: Listar, crear, editar y soft-delete cuentas.

**Archivos**:

1. `src/lib/validators.ts` — agregar accountSchema
2. `src/components/accounts/account-card.tsx`
3. `src/components/accounts/account-form.tsx`
4. `src/pages/accounts.tsx`

**Componentes shadcn**: `dialog select tabs alert-dialog`

#### accountSchema (Zod)

```typescript
{
  name: z.string().min(1, "Requerido").max(100),
  account_type: z.enum(["BANK", "WALLET", "CREDIT_CARD", "CASH"]),
  currency: z.enum(["COP", "USD", "EUR"]).default("COP"),
  color: z.string().regex(/^#[0-9A-Fa-f]{6}$/).default("#4F46E5"),
  icon: z.string().default("wallet"),
  credit_limit: z.string().optional(),
  interest_rate: z.string().optional(),
  cut_off_day: z.number().min(1).max(31).optional(),
  payment_day: z.number().min(1).max(31).optional(),
}
// .refine: si account_type === "CREDIT_CARD" → credit_limit obligatorio
```

#### AccountCard

```
<Card className="p-4">
  Layout: flex items-center gap-3
```

- Izquierda: círculo `w-10 h-10 rounded-full` con `backgroundColor: account.color` + ícono blanco centrado
- Centro: nombre `text-sm font-medium`, tipo `text-xs text-muted-foreground`
- Derecha: balance `text-sm font-bold tabular-nums`
- Badge `text-xs` con tipo de cuenta
- Si CREDIT_CARD: mostrar available_credit debajo del balance
- Botones editar (Pencil) y eliminar (Trash2): `h-8 w-8` icon buttons

#### AccountForm (Sheet en mobile / Dialog en desktop)

- Modo crear o editar (prop `account?: Account`)
- Select account_type: Cuenta Bancaria, Billetera Digital, Tarjeta de Crédito, Efectivo
- Select currency: COP, USD, EUR
- Input color hex
- Campos condicionales si account_type === "CREDIT_CARD": credit_limit, interest_rate, cut_off_day, payment_day
- Todos los inputs `h-11`
- Submit: POST crear, PATCH editar → invalidar `["accounts"]`

#### Página Cuentas

- Header: "Cuentas" + botón "Nueva cuenta" `h-10`
- Summary: balance por moneda desde `/accounts/summary/`
- Grid: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4`
- Eliminar: AlertDialog confirmación → DELETE (soft delete) → toast

**Verificación**: Crear "Davivienda" BANK → aparece en grid → editar nombre → soft delete → desaparece.

---

### FASE F4: Transacciones

**Objetivo**: Listar con filtros, crear y eliminar transacciones.

**Archivos**:

1. `src/types/category.ts`
2. `src/api/categories.ts`
3. `src/hooks/use-categories.ts`
4. `src/lib/validators.ts` — agregar transactionSchema
5. `src/components/transactions/transaction-filters.tsx`
6. `src/components/transactions/transaction-form.tsx`
7. `src/components/transactions/transaction-list.tsx`
8. `src/pages/transactions.tsx`

**Componentes shadcn**: `table tabs popover calendar command alert-dialog`

#### transactionSchema (Zod)

```typescript
{
  transaction_type: z.enum(["INCOME", "EXPENSE", "TRANSFER"]),
  amount: z.string().refine(v => parseFloat(v) > 0, "Debe ser mayor a 0"),
  description: z.string().max(255).optional(),
  date: z.string(), // "YYYY-MM-DD"
  account: z.number(),
  destination_account: z.number().optional(),
  category: z.number().optional(),
}
// .refine: si TRANSFER → destination_account obligatorio
// .refine: si TRANSFER → destination_account !== account
```

#### TransactionFilters

**Mobile (< md)**: botón "Filtros" con ícono `SlidersHorizontal` → abre Sheet bottom con filtros apilados verticalmente + botón "Aplicar" `w-full h-11` abajo.

**Desktop (≥ md)**: fila horizontal `flex flex-wrap gap-3`.

Filtros:
- Select tipo: Todos | Ingreso | Gasto | Transferencia
- Select cuenta
- Date range con Calendar/Popover
- Input búsqueda (search)

Los filtros se pasan como query params al hook `useTransactions(filters)`.

#### TransactionForm (Sheet en mobile / Dialog en desktop)

- Tabs arriba: Ingreso | Gasto | Transferencia (cambia `transaction_type` y UI)
- Campos comunes: monto (`h-11 text-xl font-bold` input), descripción, fecha (date picker), cuenta origen
- Si TRANSFER: select cuenta destino (excluir cuenta origen del listado)
- Si INCOME/EXPENSE: select categoría filtrada por tipo
  - INCOME → `GET /categories/?category_type=INCOME`
  - EXPENSE → `GET /categories/?category_type=EXPENSE`
- Cuenta y categoría con Command (combobox) de shadcn
- Todos los inputs `h-11`
- Submit → POST → invalidar `["transactions"]` y `["accounts"]`

#### TransactionList

**Mobile (< md)**: lista de items, cada uno:

```
flex items-center gap-3 py-3 border-b
```

- Izquierda: ícono por tipo en círculo `w-9 h-9 rounded-full` con fondo semántico
- Centro: descripción `text-sm font-medium` + cuenta y fecha `text-xs text-muted-foreground`
- Derecha: monto `text-sm font-bold tabular-nums` con color y signo

**Desktop (≥ md)**: tabla shadcn con columnas: Tipo (ícono), Descripción, Cuenta, Categoría, Monto, Fecha.

Colores y signos:
- INCOME: `+$3.000.000` en `text-emerald-500`
- EXPENSE: `-$50.000` en `text-red-500`
- TRANSFER: `$500.000` en `text-blue-500`

Paginación server-side: botones "Anterior" / "Siguiente" usando `next`/`previous` de la API.

Eliminar con AlertDialog de confirmación.

**Verificación**: Ingreso $1M → balance sube → gasto $50K → balance baja → transferencia → ambos balances cambian.

---

### FASE F5: Categorías

**Objetivo**: Ver, crear y gestionar categorías custom.

**Archivos**:

1. `src/lib/validators.ts` — agregar categorySchema
2. `src/components/categories/category-badge.tsx`
3. `src/components/categories/category-form.tsx`
4. `src/pages/categories.tsx`

#### categorySchema (Zod)

```typescript
{
  name: z.string().min(1, "Requerido").max(100),
  category_type: z.enum(["INCOME", "EXPENSE"]),
  icon: z.string().default("tag"),
  color: z.string().regex(/^#[0-9A-Fa-f]{6}$/).default("#6366F1"),
}
```

#### Página Categorías

- Tabs: Gastos | Ingresos
- Cada tab: `GET /categories/?category_type=EXPENSE` o `INCOME`
- Grid: `grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3`
- Cada categoría: card `p-3`, ícono con color en círculo `w-8 h-8 rounded-full`, nombre `text-sm font-medium`
- Badge "Sistema" `text-[10px]` si `is_default`
- Categorías sistema: SIN botones editar/eliminar
- Categorías custom: botones editar y eliminar
- Botón "Nueva categoría" → Sheet/Dialog

#### CategoryForm (Sheet en mobile / Dialog en desktop)

- Inputs: nombre, tipo (INCOME/EXPENSE), ícono (input texto), color (input hex con preview del color)
- Todos los inputs `h-11`
- Submit: POST → invalidar `["categories"]`

**Verificación**: Ver 20 categorías sistema → crear "Crypto" INCOME → aparece en Ingresos sin badge "Sistema" → aparece como opción al crear transacción INCOME.

---

## 8. DEPENDENCIAS EXACTAS

```bash
# Instaladas en F0
npm install react-router zustand @tanstack/react-query axios
npm install react-hook-form @hookform/resolvers zod
npm install lucide-react date-fns clsx tailwind-merge
npm install -D tailwindcss @tailwindcss/vite
```

---

## 9. ORDEN DE EJECUCIÓN

```
F0 → F1 → F2 → F3 (paralela F4) → F5
```

Cada fase depende de la anterior excepto F3 y F4 que son paralelas (ambas dependen de F2).
