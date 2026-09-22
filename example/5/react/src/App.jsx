import { useEffect, useState } from "react";

// Where the FastAPI backend is running.
const API_URL = "http://127.0.0.1:8000";

export default function App() {
  const [items, setItems] = useState([]); // the full array from the server
  const [value, setValue] = useState(""); // what's typed in the "add" box
  const [reached, setReached] = useState(null); // result of "reach by index"
  const [error, setError] = useState(null);

  const [editingIndex, setEditingIndex] = useState(null); // which row is being edited
  const [editValue, setEditValue] = useState(""); // that row's in-progress text

  // Load the array once when the page opens.
  useEffect(() => {
    loadItems();
  }, []);

  // READ — GET /items, the whole array.
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

  // CREATE — POST /items, appends one value to the array.
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
    await loadItems(); // refresh the array so the new item shows up
  }

  // REACH — GET /items/{index}, one specific array position.
  async function reachItem(index) {
    const response = await fetch(`${API_URL}/items/${index}`);
    if (!response.ok) {
      setError(`Failed to reach index ${index} (status ${response.status})`);
      setReached(null);
      return;
    }
    setReached(await response.json());
    setError(null);
  }

  function startEditing(index, currentValue) {
    setEditingIndex(index);
    setEditValue(currentValue);
  }

  // UPDATE — PUT or PATCH /items/{index}, depending which button was
  // clicked. Both send the same body here (this item only has one
  // field), but the HTTP method itself is what differs.
  async function saveEdit(index, method) {
    const response = await fetch(`${API_URL}/items/${index}`, {
      method: method, // "PUT" or "PATCH"
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value: editValue }),
    });

    if (!response.ok) {
      setError(`Failed to update item (status ${response.status})`);
      return;
    }

    setEditingIndex(null);
    await loadItems();
  }

  // DELETE — DELETE /items/{index}, removes that entry.
  async function deleteItem(index) {
    const response = await fetch(`${API_URL}/items/${index}`, {
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
      <h1>Array Store</h1>

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

      {/* READ: the whole array, one <li> per item via .map() */}
      <ul style={{ listStyle: "none", padding: 0, marginTop: "1.5rem" }}>
        {items.map((item, index) =>
          editingIndex === index ? (
            <li
              key={index}
              style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.25rem 0" }}
            >
              <span style={{ color: "#888", width: "1.5rem" }}>{index}</span>
              <input
                value={editValue}
                onChange={(event) => setEditValue(event.target.value)}
                style={{ flex: 1, padding: "0.25rem" }}
              />
              <button onClick={() => saveEdit(index, "PUT")}>Save (PUT)</button>
              <button onClick={() => saveEdit(index, "PATCH")}>Save (PATCH)</button>
              <button onClick={() => setEditingIndex(null)}>Cancel</button>
            </li>
          ) : (
            <li
              key={index}
              style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.25rem 0" }}
            >
              <span style={{ color: "#888", width: "1.5rem" }}>{index}</span>
              <span style={{ flex: 1 }}>{item}</span>
              {/* REACH: fetches this one index directly from the backend,
                  instead of just reading it from the array already in state */}
              <button onClick={() => reachItem(index)}>Reach</button>
              <button onClick={() => startEditing(index, item)}>Edit</button>
              <button onClick={() => deleteItem(index)}>Delete</button>
            </li>
          ),
        )}
      </ul>

      {items.length === 0 && !error && <p>Array is empty — add something above.</p>}

      {reached && (
        <p style={{ marginTop: "1rem" }}>
          Reached index <strong>{reached.index}</strong>:{" "}
          <strong>{reached.value}</strong>
        </p>
      )}
    </main>
  );
}
