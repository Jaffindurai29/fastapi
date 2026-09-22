import { useEffect, useState } from "react";

// Where the FastAPI backend is running.
const API_URL = "http://127.0.0.1:8000";

export default function App() {
  const [items, setItems] = useState([]); // rows from the database, each { id, value }
  const [value, setValue] = useState(""); // what's typed in the "add" box
  const [reached, setReached] = useState(null); // result of "reach by id"
  const [error, setError] = useState(null);

  const [editingId, setEditingId] = useState(null); // which row's id is being edited
  const [editValue, setEditValue] = useState(""); // that row's in-progress text

  // Load every row once when the page opens.
  useEffect(() => {
    loadItems();
  }, []);

  // READ — GET /items, every row.
  async function loadItems() {
    try {
      const response = await fetch(`${API_URL}/items`);
      if (!response.ok) {
        throw new Error(`Failed to load items (status ${response.status})`);
      }
      setItems(await response.json());
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }

  // CREATE — POST /items, inserts a new row. The database assigns the id.
  async function addItem(event) {
    event.preventDefault();
    if (value.trim() === "") return;

    const response = await fetch(`${API_URL}/items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value: value }),
    });

    if (!response.ok) {
      setError(`Failed to add item (status ${response.status})`);
      return;
    }

    setValue("");
    await loadItems();
  }

  // REACH — GET /items/{id}, one specific row by its real database id
  // (not its position in the list — deleting a row never renumbers
  // anyone else's id, unlike the plain-array version of this topic).
  async function reachItem(id) {
    const response = await fetch(`${API_URL}/items/${id}`);
    if (!response.ok) {
      setError(`Failed to reach id ${id} (status ${response.status})`);
      setReached(null);
      return;
    }
    setReached(await response.json());
    setError(null);
  }

  function startEditing(id, currentValue) {
    setEditingId(id);
    setEditValue(currentValue);
  }

  // UPDATE — PUT or PATCH /items/{id}, depending which button was
  // clicked. Both send the same body here (this row only has one
  // field), but the HTTP method itself is what differs.
  async function saveEdit(id, method) {
    const response = await fetch(`${API_URL}/items/${id}`, {
      method: method, // "PUT" or "PATCH"
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value: editValue }),
    });

    if (!response.ok) {
      setError(`Failed to update item (status ${response.status})`);
      return;
    }

    setEditingId(null);
    await loadItems();
  }

  // DELETE — DELETE /items/{id}, removes that row.
  async function deleteItem(id) {
    const response = await fetch(`${API_URL}/items/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      setError(`Failed to delete item (status ${response.status})`);
      return;
    }

    await loadItems();
  }

  return (
    <main style={{ maxWidth: 560, margin: "3rem auto", fontFamily: "sans-serif" }}>
      <h1>MySQL Store</h1>

      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {/* CREATE form */}
      <form onSubmit={addItem} style={{ display: "flex", gap: "0.5rem" }}>
        <input
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Add a value"
          style={{ flex: 1, padding: "0.5rem" }}
        />
        <button type="submit">Add</button>
      </form>

      {/* READ: every row, one <li> per row via .map() */}
      <ul style={{ listStyle: "none", padding: 0, marginTop: "1.5rem" }}>
        {items.map((item) =>
          editingId === item.id ? (
            <li
              key={item.id}
              style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.25rem 0" }}
            >
              <span style={{ color: "#888", width: "2rem" }}>#{item.id}</span>
              <input
                value={editValue}
                onChange={(event) => setEditValue(event.target.value)}
                style={{ flex: 1, padding: "0.25rem" }}
              />
              <button onClick={() => saveEdit(item.id, "PUT")}>Save (PUT)</button>
              <button onClick={() => saveEdit(item.id, "PATCH")}>Save (PATCH)</button>
              <button onClick={() => setEditingId(null)}>Cancel</button>
            </li>
          ) : (
            <li
              key={item.id}
              style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.25rem 0" }}
            >
              <span style={{ color: "#888", width: "2rem" }}>#{item.id}</span>
              <span style={{ flex: 1 }}>{item.value}</span>
              {/* REACH: fetches this one id directly from the backend,
                  instead of just reading it from what's already in state */}
              <button onClick={() => reachItem(item.id)}>Reach</button>
              <button onClick={() => startEditing(item.id, item.value)}>Edit</button>
              <button onClick={() => deleteItem(item.id)}>Delete</button>
            </li>
          ),
        )}
      </ul>

      {items.length === 0 && !error && <p>No rows yet — add something above.</p>}

      {reached && (
        <p style={{ marginTop: "1rem" }}>
          Reached id <strong>#{reached.id}</strong>: <strong>{reached.value}</strong>
        </p>
      )}
    </main>
  );
}
