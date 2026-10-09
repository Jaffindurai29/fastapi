# 14/react — Role-protected routes, step by step

[12/react](../../12/react/STEPS.md) was one screen. A shop has many
pages, and which ones you may open depends on your role. This
walkthrough covers the four new pieces: the router, the auth context,
`ProtectedRoute`, and the role-based navbar. The pages themselves are
ordinary React forms and lists calling the API.

1. **`api.js` — one axios instance for everything.** Pages call
   `api.get("/orders/mine")` and never think about tokens. Two
   interceptors do the work, as in 12/react:

   - **Request:** add `Authorization: Bearer <access token>`.
   - **Response:** on a `401`, swap the refresh token for a new access
     token and replay the request once. If the refresh fails too, clear
     the tokens and call `onSessionExpired()`.

   ```js
   refreshing ??= axios
     .post(`${API_URL}/refresh`, { refresh_token: tokens.refresh_token })
     .finally(() => {
       refreshing = null;
     });
   ```

   `refreshing` is shared, so three requests failing at once cause one
   `/refresh` call, not three. Both tokens live in `localStorage`, so a
   reload keeps you logged in. (12/react explains the trade-off: any
   script on the page can read `localStorage`.)

2. **`auth.jsx` — who is logged in, for the whole app.** `AuthProvider`
   holds `user` (`{ id, username, role }`) and gives every component
   `login()` and `logout()` through `useAuth()`.

   ```js
   const res = await axios.post(`${API_URL}/login`, { username, password });
   tokenStore.set(res.data);
   // The role comes from /me (the database), not from decoding the token.
   const me = await api.get("/me");
   setUser(me.data);
   ```

   On page load, if tokens are saved, it calls `/me` before deciding
   anything. Until that answer arrives, `checking` is `true`, so the app
   doesn't flash the login page at someone who is logged in.

3. **`App.jsx` — every route in one place.**

   ```jsx
   <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
     <Route index element={<Home />} />
     <Route path="products" element={customerOnly(<ProductsPage />)} />
     <Route path="admin/users" element={adminOnly(<AdminUsersPage />)} />
     ...
   </Route>
   ```

   The outer route needs any login and draws the navbar (`Layout`). The
   inner routes add a role on top. `customerOnly` / `adminOnly` are
   just short ways to write `<ProtectedRoute roles={["admin"]}>`.

4. **`ProtectedRoute.jsx` — two checks, two redirects.**

   ```jsx
   if (!user) {
     return <Navigate to="/login" replace state={{ from: location.pathname }} />;
   }
   if (roles && !roles.includes(user.role)) {
     return <Navigate to="/forbidden" replace />;
   }
   return children;
   ```

   The same split as the backend: not logged in (`401`) → login page;
   logged in but wrong role (`403`) → forbidden page. `state.from`
   remembers where you were going, and `LoginPage` sends you back there
   after login.

5. **The frontend check is not security.** Anyone can open DevTools and
   change `user.role` to `"admin"`, and the admin pages will render.
   Every request they make still gets `403` from `require_roles("admin")`
   on the backend. `ProtectedRoute` only decides what to **show**; the
   API decides what is **allowed**.

6. **`Layout.jsx` — a navbar per role.**

   ```js
   const LINKS = {
     customer: [{ to: "/products", label: "Shop" }, { to: "/orders", label: "My orders" }],
     admin: [{ to: "/admin/products", label: "Products" }, ...],
   };
   ```

   Hiding links is a convenience, not protection: typing the URL still
   hits `ProtectedRoute`, and the API behind it still checks the role.
   `<Outlet />` is where the matching child route renders.

7. **`homeFor(user)` — where each role lands.** `/` redirects customers
   to `/products` and admins to `/admin/products`. `LoginPage` and
   `ForbiddenPage` use the same function.

8. **Pages show the backend's reason.** `errorText(err)` reads FastAPI's
   `detail`, so a failed order shows "Only 0 of Sticker pack left"
   instead of a generic error. The cart total is only a preview; the
   backend computes the real total from its own prices.

9. **`AdminOrdersPage.jsx` mirrors `NEXT_STATUS`.** It shows "Mark
   shipped" and "Mark cancelled" for a pending order, "Mark delivered"
   for a shipped one. The backend enforces the same table, so even a
   hand-made request can't jump from `pending` to `delivered`.
