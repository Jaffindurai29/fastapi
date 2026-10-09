import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, homeFor, useAuth } from "./auth";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminOrdersPage from "./pages/AdminOrdersPage";
import AdminProductsPage from "./pages/AdminProductsPage";
import AdminUsersPage from "./pages/AdminUsersPage";
import ForbiddenPage from "./pages/ForbiddenPage";
import LoginPage from "./pages/LoginPage";
import MyOrdersPage from "./pages/MyOrdersPage";
import ProductsPage from "./pages/ProductsPage";

function Home() {
  const { user } = useAuth();
  return <Navigate to={homeFor(user)} replace />;
}

const customerOnly = (page) => <ProtectedRoute roles={["customer"]}>{page}</ProtectedRoute>;
const adminOnly = (page) => <ProtectedRoute roles={["admin"]}>{page}</ProtectedRoute>;

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<LoginPage startMode="register" />} />

          {/* Everything below needs a login; some pages also need a role. */}
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Home />} />
            <Route path="products" element={customerOnly(<ProductsPage />)} />
            <Route path="orders" element={customerOnly(<MyOrdersPage />)} />
            <Route path="admin/products" element={adminOnly(<AdminProductsPage />)} />
            <Route path="admin/orders" element={adminOnly(<AdminOrdersPage />)} />
            <Route path="admin/users" element={adminOnly(<AdminUsersPage />)} />
            <Route path="forbidden" element={<ForbiddenPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
