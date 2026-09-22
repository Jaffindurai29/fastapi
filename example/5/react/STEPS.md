# 5/react — React frontend, step by step

This is how `App.jsx` is built up, one CRUD operation at a time. Each
step adds one thing on top of the last.

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
```

`event.preventDefault()` stops the browser's default "reload the page"
behavior on form submit. After a successful `POST`, it clears the input
and reloads the list — the new item comes from the server's response to
`loadItems()`, not from guessing what index it landed at.

## Step 4 — Reach: fetch one item by index

```jsx
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
```

Stored in its own `reached` state, separate from `items` — so it's
visibly a fresh fetch, not just re-reading something already on the
page.

## Step 5 — Update: edit mode, with two save buttons

```jsx
function startEditing(index, currentValue) {
  setEditingIndex(index);
  setEditValue(currentValue);
}

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
```

`saveEdit` takes `method` as a parameter on purpose — clicking **Save
(PUT)** and **Save (PATCH)** call the exact same function with a
different string, proving both HTTP methods are genuinely wired up to
the backend, not just one button pretending to be the other.

## Step 6 — Delete

```jsx
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
```

The simplest of the five — no body, just a method and a URL.

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
