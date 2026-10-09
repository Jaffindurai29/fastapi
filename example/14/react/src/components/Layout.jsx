import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

const LINKS = {
  customer: [
    { to: "/products", label: "Shop" },
    { to: "/orders", label: "My orders" },
  ],
  admin: [
    { to: "/admin/products", label: "Products" },
    { to: "/admin/orders", label: "Orders" },
    { to: "/admin/users", label: "Users" },
  ],
};

// The navbar only shows links the user's role can open.
export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <>
      <nav className="navbar">
        <span className="brand">MiniShop</span>
        <div className="nav-links">
          {LINKS[user.role].map((link) => (
            <NavLink key={link.to} to={link.to} className="nav-link">
              {link.label}
            </NavLink>
          ))}
        </div>
        <div className="nav-user">
          <span>{user.username}</span>
          <span className={`badge role-${user.role}`}>{user.role}</span>
          <button className="btn small secondary" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </nav>
      <main className="container">
        <Outlet />
      </main>
    </>
  );
}
