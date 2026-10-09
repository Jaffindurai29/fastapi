# 14/react — Shop UI with role-protected routes

A React frontend for the shop API in [14/a](../a). Customers browse
products, fill a cart and place orders; admins manage products, stock,
orders and users. Each role only sees its own pages, enforced by one
`<ProtectedRoute roles={[...]}>` component. See [STEPS.md](STEPS.md)
for a step-by-step walkthrough.

New compared to [12/react](../../12/react): **React Router** (several
pages with real URLs) and **routes protected by role**.

```
react/
├── src/api.js                       # axios instance, token storage, refresh interceptor
├── src/auth.jsx                     # AuthProvider: who is logged in, login(), logout()
├── src/App.jsx                      # every route, and which role may open it
├── src/components/ProtectedRoute.jsx  # logged out → /login, wrong role → /forbidden
├── src/components/Layout.jsx        # navbar with only your role's links
├── src/components/OrderCard.jsx     # one order (used by customers and admins)
├── src/pages/LoginPage.jsx          # login + register tabs
├── src/pages/ProductsPage.jsx       # customer: products + cart + checkout
├── src/pages/MyOrdersPage.jsx       # customer: own orders, cancel pending ones
├── src/pages/AdminProductsPage.jsx  # admin: add, price, stock, hide/show
├── src/pages/AdminOrdersPage.jsx    # admin: all orders, change status
├── src/pages/AdminUsersPage.jsx     # admin: change roles
├── src/pages/ForbiddenPage.jsx      # 403 page
└── src/main.jsx
```

## 1. Run the backend

```bash
cd example/14/a
uvicorn main:app --reload
```

## 2. Run the frontend

In a separate terminal:

```bash
cd example/14/react
npm install
npm run dev
```

Open the URL Vite prints (usually
[http://localhost:5173](http://localhost:5173)). The backend allows
`localhost:5173` and `127.0.0.1:5173`.

## Pages

| URL | Who | What |
|---|---|---|
| `/login`, `/register` | anyone | Login and register tabs |
| `/products` | customer | Product grid, cart, phone + address, **Place order** |
| `/orders` | customer | Your orders; **Cancel order** while pending |
| `/admin/products` | admin | Add products, edit price, `+5` / `-2` stock, hide/show |
| `/admin/orders` | admin | Every order with decrypted phone and address; **Mark shipped / delivered / cancelled** |
| `/admin/users` | admin | Every user; change role (not your own) |
| `/forbidden` | logged in | "Your role can't open that page" |

## What to try

| Do this | What you'll see |
|---|---|
| Open `/admin/products` while logged out | Sent to `/login`; after logging in as `admin` you land back on `/admin/products` |
| Log in as `alice` / `alice-password` | Shop and My orders in the navbar, nothing else |
| As alice, type `/admin/users` in the address bar | Sent to `/forbidden` |
| Buy the **Sticker pack** (stock 1) | Order placed; the product now shows "Out of stock" |
| As bob, try to buy it in a tab opened earlier | "Only 0 of Sticker pack left" and the list reloads |
| Cancel a pending order | Status `cancelled`, stock goes back up |
| Log in as `admin` / `admin-password` | Products, Orders, Users in the navbar; phone and address readable |
| Mark an order **shipped** | The customer can no longer cancel it |
| Hide a product | Greyed out for admin, gone from the customer's shop |
| Promote bob to admin, then reload bob's tab | Bob's menu switches to the admin pages |
| Reload the page while logged in | Still logged in: tokens are in `localStorage` |
