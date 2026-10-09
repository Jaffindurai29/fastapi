import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { API_URL, errorText } from "../api";
import { homeFor, useAuth } from "../auth";

export default function LoginPage({ startMode = "login" }) {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [mode, setMode] = useState(startMode); // 'login' or 'register'
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [notice, setNotice] = useState(null); // { type: 'ok' | 'error', text }
  const [loading, setLoading] = useState(false);

  const isLogin = mode === "login";

  // Already logged in? Skip the form.
  if (user) return <Navigate to={homeFor(user)} replace />;

  function switchMode(newMode) {
    setMode(newMode);
    setNotice(null);
    setPassword("");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setNotice(null);

    try {
      if (isLogin) {
        const me = await login(username, password);
        // Back to the page they tried to open, or their role's home page.
        navigate(location.state?.from || homeFor(me), { replace: true });
      } else {
        await axios.post(`${API_URL}/register`, { username, password });
        setNotice({ type: "ok", text: "Account created! You can log in now." });
        setMode("login");
        setPassword("");
      }
    } catch (err) {
      // axios throws on 4xx/5xx: wrong password (401), username taken (409),
      // password too short (422), or the backend isn't running.
      setNotice({ type: "error", text: errorText(err) });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="card">
        <h1>{isLogin ? "Welcome back" : "Create account"}</h1>
        <p className="subtitle">{isLogin ? "Log in to continue" : "Sign up in a few seconds"}</p>

        <div className="tabs">
          <button
            type="button"
            className={isLogin ? "tab active" : "tab"}
            onClick={() => switchMode("login")}
          >
            Login
          </button>
          <button
            type="button"
            className={!isLogin ? "tab active" : "tab"}
            onClick={() => switchMode("register")}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <label>
            Username
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. alice"
              minLength={isLogin ? undefined : 3}
              maxLength={30}
              required
              autoComplete="username"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={isLogin ? "Your password" : "At least 8 characters"}
              minLength={isLogin ? undefined : 8}
              maxLength={128}
              required
              autoComplete={isLogin ? "current-password" : "new-password"}
            />
          </label>

          {notice && <div className={`alert ${notice.type}`}>{notice.text}</div>}

          <button className="btn" type="submit" disabled={loading}>
            {loading ? "Please wait…" : isLogin ? "Log in" : "Register"}
          </button>
        </form>
      </div>
    </div>
  );
}
