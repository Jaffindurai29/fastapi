# 5/react — React frontend, step by step

This is how `App.jsx` is built up, one CRUD operation at a time. Each
step adds one thing on top of the last.

## Step 0 — Setup: axios and one error helper

```bash
npm install axios
```

```jsx
import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

// axios throws for any non-2xx response, so every call below lives in a
// try/catch. This turns the thrown error into a readable message.
function errorMessage(action, err) {
  const status = err.response?.status;
  return status ? `Failed to ${action} (status ${status})` : `Failed to ${action}: ${err.message}`;
}
```

Every request in this app goes through [axios](https://axios-http.com)
instead of the browser's built-in `fetch()`. Three differences matter
here:

| | `fetch()` | `axios` |
|---|---|---|
| Response body | `await response.json()` | already parsed, in `response.data` |
| Sending JSON | `JSON.stringify(body)` + a `Content-Type` header | pass the object, axios does both |
| 404 / 500 | resolves normally, you check `response.ok` | **throws** — handled in `catch` |

That last row is why `errorMessage` exists: when the server answers
with an error, axios puts the status on `err.response.status`. When the
server can't be reached at all (backend not running, CORS blocked),
there's no `err.response`, so it falls back to `err.message`.

## Step 1 — State: what the page needs to remember

```jsx
const [items, setItems] = useState([]);       // the full array from the server
const [value, setValue] = useState("");       // what's typed in the "add" box
const [reached, setReached] = useState(null); // result of "reach by index"
const [error, setError] = useState(null);

const [editingIndex, setEditingIndex] = useState(null); // which row is being edited
const [editValue, setEditValue] = useState("");         // that row's in-progress text
```

Six pieces of state, one per thing the UI needs to track between
re-renders. `editingIndex`/`editValue` exist only for the Update step —
everything else exists from the start.

## Step 2 — Read: load the array on page open

```jsx
useEffect(() => {
  loadItems();
}, []);

async function loadItems() {
  try {
    const response = await axios.get(`${API_URL}/items`);
    setItems(response.data); // axios already parsed the JSON
    setError(null);
  } catch (err) {
    setError(errorMessage("load items", err));
  }
}
```

`useEffect(..., [])` runs once, right after the first render — that's
what loads the starting list. `loadItems` is also called again after
every other operation below, so the page always reflects what the
server actually has, not just an optimistic guess.

## Step 3 — Create: the add form

```jsx
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
```

`event.preventDefault()` stops the browser's default "reload the page"
behavior on form submit. `axios.post(url, body)` takes the body as a
plain object — no `JSON.stringify`, no headers. The `return` inside
`catch` matters: on failure it stops before clearing the input, so the
user doesn't lose what they typed. After a successful `POST`, it clears the input
and reloads the list — the new item comes from the server's response to
`loadItems()`, not from guessing what index it landed at.

## Step 4 — Reach: fetch one item by index

```jsx
async function reachItem(index) {
  try {
    const response = await axios.get(`${API_URL}/items/${index}`);
    setReached(response.data);
    setError(null);
  } catch (err) {
    setError(errorMessage(`reach index ${index}`, err));
    setReached(null);
  }
}
```

Stored in its own `reached` state, separate from `items` — so it's
visibly a fresh request, not just re-reading something already on the
page. An index that doesn't exist gets a `404` from the backend, which
axios throws, which lands in `catch` as "Failed to reach index 7
(status 404)".

## Step 5 — Update: edit mode, with two save buttons

```jsx
function startEditing(index, currentValue) {
  setEditingIndex(index);
  setEditValue(currentValue);
}

async function saveEdit(index, method) {
  try {
    await axios({
      method: method, // "PUT" or "PATCH"
      url: `${API_URL}/items/${index}`,
      data: { value: editValue },
    });
  } catch (err) {
    setError(errorMessage("update item", err));
    return;
  }

  setEditingIndex(null);
  await loadItems();
}
```

`saveEdit` takes `method` as a parameter on purpose — clicking **Save
(PUT)** and **Save (PATCH)** call the exact same function with a
different string, proving both HTTP methods are genuinely wired up to
the backend, not just one button pretending to be the other.

That's also why this step calls `axios({ method, url, data })` instead
of the shortcut methods. `axios.put(url, data)` and
`axios.patch(url, data)` exist too, but they bake the method into the
function name. The config-object form lets the method be a variable.

## Step 6 — Delete

```jsx
async function deleteItem(index) {
  try {
    await axios.delete(`${API_URL}/items/${index}`);
  } catch (err) {
    setError(errorMessage("delete item", err));
    return;
  }

  await loadItems();
}
```

The simplest of the five — no body, just `axios.delete(url)`.

## Step 7 — Rendering it all

```jsx
{items.map((item, index) =>
  editingIndex === index ? (
    <li key={index}>
      {/* edit mode: input + Save (PUT) + Save (PATCH) + Cancel */}
    </li>
  ) : (
    <li key={index}>
      {/* normal mode: value + Reach + Edit + Delete */}
    </li>
  ),
)}
```

One `<li>` per array entry, switching between two layouts depending on
whether `editingIndex === index` — that's the whole mechanism behind
"click Edit, that one row turns into an input box, the rest don't."

See [example/7/react/STEPS.md](../../7/react/STEPS.md) for what changes
when this same UI points at a MySQL backend instead of a plain array.
