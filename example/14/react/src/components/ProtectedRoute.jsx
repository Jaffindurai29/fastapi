import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth";

// <ProtectedRoute>               → any logged-in user
// <ProtectedRoute roles={['admin']}> → admins only
//
// This only decides what the browser SHOWS. Anyone can edit frontend
// code, so the real protection is require_roles() on the backend.
export default function ProtectedRoute({ roles, children }) {
  const { user, checking } = useAuth();
  const location = useLocation();

  if (checking) return <p className="center-note">Loading…</p>;

  if (!user) {
    // Remember where they were going, so login can send them back.
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/forbidden" replace />;
  }

  return children;
}
