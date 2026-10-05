import { useEffect, useState } from "react";
import { api, breakAccessToken, clearTokens, restoreSession, saveTokens, setOnLogout } from "./api.js";

// Turns an axios error into something a person can read. The backend's
// own `detail` message is usually the best explanation.
function errorMessage(action, err) {
  const status = err.response?.status;
  const detail = err.response?.data?.detail;
  if (status === 429) return "Too many login attempts. Wait a minute and try again.";
  if (status === 403) return `Not allowed: ${detail ?? "forbidden"}`;
  if (status && typeof detail === "string") return `Failed to ${action}: ${detail}`;
  return status ? `Failed to ${action} (status ${status})` : `Failed to ${action}: ${err.message}`;
}

const rowStyle = { display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.25rem 0" };

export default function App() {
  const [user, setUser] = useState(null); // { id, username, role } once logged in
  const [username, setUsername] = useState("alice");
  const [password, setPassword] = useState("alice-password");

  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState(""); // the "add note" box
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");

  const [adminUsers, setAdminUsers] = useState(null); // result of GET /admin/users
  const [error, setError] = useState(null);
  const [info, setInfo] = useState(null);

  // On page load: tell api.js what "logged out" means for the UI, then try
  // to turn a saved refresh token back into a session.
  useEffect(() => {
    setOnLogout(() => {
      resetState();
      setError("Your session expired. Please log in again.");
    });
    restoreSession().then((ok) => {
      if (ok) loadUserAndNotes();
    });
  }, []);

  function resetState() {
    setUser(null);
    setNotes([]);
    setAdminUsers(null);
    setEditingId(null);
  }

  async function loadUserAndNotes() {
    try {
      const me = await api.get("/users/me");
      setUser(me.data);
      await loadNotes();
    } catch (err) {
      setError(errorMessage("load your account", err));
    }
  }

  // LOGIN — POST /token. OAuth2 says the body is a FORM, not JSON.
  // URLSearchParams makes axios send it as
  // application/x-www-form-urlencoded: username=alice&password=...
  async function login(event) {
    event.preventDefault();
    try {
      const body = new URLSearchParams({ username, password });
      const response = await api.post("/token", body);
      saveTokens(response.data);
      setError(null);
      setInfo(null);
      await loadUserAndNotes();
    } catch (err) {
      setError(errorMessage("log in", err));
    }
  }

  // LOGOUT — forget the tokens. (The access token still works on the
  // server until it expires; that's why it's short-lived.)
  function logout() {
    clearTokens();
    resetState();
    setError(null);
    setInfo(null);
  }

  // READ — GET /notes. The backend decides what "your notes" means:
  // your own, or everyone's for an admin.
  async function loadNotes() {
    try {
      const response = await api.get("/notes");
      setNotes(response.data);
      setError(null);
    } catch (err) {
      setError(errorMessage("load notes", err));
    }
  }

  // CREATE — POST /notes. No owner_id sent: the server uses whoever the
  // token belongs to.
  async function addNote(event) {
    event.preventDefault();
    if (title.trim() === "") return;
    try {
      await api.post("/notes", { title, body: "" });
    } catch (err) {
      setError(errorMessage("add note", err));
      return;
    }
    setTitle("");
    await loadNotes();
  }

  // UPDATE — PUT /notes/{id}
  async function saveEdit(note) {
    try {
      await api.put(`/notes/${note.id}`, { title: editTitle, body: note.body });
    } catch (err) {
      setError(errorMessage("update note", err));
      return;
    }
    setEditingId(null);
    await loadNotes();
  }

  // DELETE — DELETE /notes/{id}
  async function deleteNote(id) {
    try {
      await api.delete(`/notes/${id}`);
    } catch (err) {
      setError(errorMessage("delete note", err));
      return;
    }
    await loadNotes();
  }

  // Ask for a note by id, including ones that aren't yours, to see the 403.
  async function readNoteById(id) {
    try {
      const response = await api.get(`/notes/${id}`);
      setInfo(`Note #${response.data.id}: ${response.data.title}`);
      setError(null);
    } catch (err) {
      setError(errorMessage(`read note #${id}`, err));
      setInfo(null);
    }
  }

  // ADMIN — GET /admin/users. Admins get the list; everyone else gets 403.
  async function loadAdminUsers() {
    try {
      const response = await api.get("/admin/users");
      setAdminUsers(response.data);
      setError(null);
    } catch (err) {
      setError(errorMessage("load users", err));
      setAdminUsers(null);
    }
  }

  // DEMO — make the next request fail with 401, so the response
  // interceptor in api.js refreshes the tokens and retries it.
  async function simulateExpiredToken() {
    breakAccessToken();
    await loadNotes();
    setInfo("Access token was invalid, so api.js refreshed it and retried. You didn't notice a thing.");
  }

  // ---- Logged out: show the login form ----
  if (!user) {
    return (
      <main style={{ maxWidth: 560, margin: "3rem auto", fontFamily: "sans-serif" }}>
        <h1>Secure Notes</h1>
        {error && <p style={{ color: "crimson" }}>{error}</p>}

        <form onSubmit={login} style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="Username"
            style={{ padding: "0.5rem" }}
          />
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Password"
            style={{ padding: "0.5rem" }}
          />
          <button type="submit">Log in</button>
        </form>

        <p style={{ color: "#888" }}>
          Try alice / alice-password, bob / bob-password, or admin / admin-password. Get the password wrong 6 times
          in a minute to see the rate limit.
        </p>
      </main>
    );
  }

  // ---- Logged in ----
  const isAdmin = user.role === "admin";

  return (
    <main style={{ maxWidth: 560, margin: "3rem auto", fontFamily: "sans-serif" }}>
      <h1>Secure Notes</h1>

      <div style={rowStyle}>
        <span style={{ flex: 1 }}>
          Logged in as <strong>{user.username}</strong> ({user.role})
          {isAdmin && (
            <span
              style={{ marginLeft: "0.5rem", padding: "0 0.4rem", background: "#1a1a1a", color: "#fff", borderRadius: 4 }}
            >
              ADMIN
            </span>
          )}
        </span>
        <button onClick={logout}>Log out</button>
      </div>

      {error && <p style={{ color: "crimson" }}>{error}</p>}
      {info && <p style={{ color: "seagreen" }}>{info}</p>}

      {/* CREATE form */}
      <form onSubmit={addNote} style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="New note title"
          style={{ flex: 1, padding: "0.5rem" }}
        />
        <button type="submit">Add</button>
      </form>

      {/* READ: one <li> per note */}
      <ul style={{ listStyle: "none", padding: 0, marginTop: "1.5rem" }}>
        {notes.map((note) =>
          editingId === note.id ? (
            <li key={note.id} style={rowStyle}>
              <span style={{ color: "#888", width: "2rem" }}>#{note.id}</span>
              <input
                value={editTitle}
                onChange={(event) => setEditTitle(event.target.value)}
                style={{ flex: 1, padding: "0.25rem" }}
              />
              <button onClick={() => saveEdit(note)}>Save</button>
              <button onClick={() => setEditingId(null)}>Cancel</button>
            </li>
          ) : (
            <li key={note.id} style={rowStyle}>
              <span style={{ color: "#888", width: "2rem" }}>#{note.id}</span>
              <span style={{ flex: 1 }}>
                {note.title}
                {/* Admins see everyone's notes, so show whose this is. */}
                {note.owner_id !== user.id && (
                  <span style={{ color: "#888" }}> (user #{note.owner_id})</span>
                )}
              </span>
              <button
                onClick={() => {
                  setEditingId(note.id);
                  setEditTitle(note.title);
                }}
              >
                Edit
              </button>
              <button onClick={() => deleteNote(note.id)}>Delete</button>
            </li>
          ),
        )}
      </ul>

      {notes.length === 0 && <p>No notes yet. Add one above.</p>}

      {/* Security experiments */}
      <h2 style={{ fontSize: "1.1rem", marginTop: "2rem" }}>Try the security rules</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
        {/* Note 3 belongs to bob: alice gets 403, bob and admin get the note. */}
        <button onClick={() => readNoteById(3)}>Read note #3</button>
        {isAdmin ? (
          <button onClick={loadAdminUsers}>Load all users (admin)</button>
        ) : (
          <button onClick={loadAdminUsers}>Try admin route</button>
        )}
        <button onClick={simulateExpiredToken}>Simulate expired access token</button>
      </div>

      {adminUsers && (
        <ul style={{ marginTop: "1rem" }}>
          {adminUsers.map((u) => (
            <li key={u.id}>
              #{u.id} {u.username} ({u.role}){!u.is_active && " (inactive)"}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
