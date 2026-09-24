import { useEffect, useState } from "react";
import axios from "axios";

// Where the FastAPI backend is running.
const API_URL = "http://127.0.0.1:8000";

// axios throws for any non-2xx response, so every call below lives in a
// try/catch. This turns the thrown error into a readable message.
function errorMessage(action, err) {
  const status = err.response?.status;
  return status ? `Failed to ${action} (status ${status})` : `Failed to ${action}: ${err.message}`;
}

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
      const response = await axios.get(`${API_URL}/items`);
      setItems(response.data); // axios already parsed the JSON
      setError(null);
    } catch (err) {
      setError(errorMessage("load items", err));
    }
  }

  // CREATE — POST /items, inserts a new row. The database assigns the id.
  async function addItem(event) {
    event.preventDefault();
    if (value.trim() === "") return;

    try {
      // axios turns the object into JSON and sets Content-Type for us.
      await axios.post(`${API_URL}/items`, { value: value });
    } catch (err) {
      setError(errorMessage("add item", err));
      return;
    }

    setValue("");
    await loadItems();
  }

  // REACH — GET /items/{id}, one specific row by its real database id
  // (not its position in the list — deleting a row never renumbers
  // anyone else's id, unlike the plain-array version of this topic).
  async function reachItem(id) {
    try {
      const response = await axios.get(`${API_URL}/items/${id}`);
      setReached(response.data);
      setError(null);
    } catch (err) {
      setError(errorMessage(`reach id ${id}`, err));
      setReached(null);
    }
  }

  function startEditing(id, currentValue) {
    setEditingId(id);
    setEditValue(currentValue);
  }

  // UPDATE — PUT or PATCH /items/{id}, depending which button was
  // clicked. Both send the same body here (this row only has one
  // field), but the HTTP method itself is what differs.
  async function saveEdit(id, method) {
    try {
      await axios({
        method: method, // "PUT" or "PATCH"
        url: `${API_URL}/items/${id}`,
        data: { value: editValue },
      });
    } catch (err) {
      setError(errorMessage("update item", err));
      return;
    }

    setEditingId(null);
    await loadItems();
  }

  // DELETE — DELETE /items/{id}, removes that row.
  async function deleteItem(id) {
    try {
      await axios.delete(`${API_URL}/items/${id}`);
    } catch (err) {
      setError(errorMessage("delete item", err));
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
