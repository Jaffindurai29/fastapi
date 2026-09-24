# 7/react — React frontend (MySQL), step by step

This is the exact same app as [5/react](../../5/react/STEPS.md), pointed
at the MySQL backend from [7/a](../a) instead of the array backend from
[5/a](../../5/a). Every step below is identical in shape — the diff is
always the same one change: **index → id**.

Both apps make their requests with axios, set up the same way — see
[Step 0 in 5/react](../../5/react/STEPS.md) for the `fetch()` vs
axios differences and the `errorMessage` helper.

## Step 1 — State

```jsx
const [items, setItems] = useState([]);       // rows from the database, each { id, value }
const [value, setValue] = useState("");
const [reached, setReached] = useState(null); // result of "reach by id"
const [error, setError] = useState(null);

const [editingId, setEditingId] = useState(null); // which row's id is being edited
const [editValue, setEditValue] = useState("");
```

**Difference from 5/react:** `editingIndex` → `editingId`. Same idea,
renamed to match what it actually holds now — a database ID, not a
position in an array. `items` also changed shape: each entry is now
`{ id, value }` instead of a plain string.

## Step 2 — Read

Identical to [5/react](../../5/react/STEPS.md) — `GET /items`, no
changes at all. The backend returns objects instead of plain strings,
but `loadItems()` doesn't need to know or care about that; it just
stores whatever JSON comes back.

## Step 3 — Create

Identical to 5/react too — `POST /items` with `{ value }`. **The one
thing that changed happened on the backend, not here:** the database
now assigns a real `id` to the new row, instead of the frontend
assuming it landed at `items.length`.

## Step 4 — Reach

```jsx
async function reachItem(id) {
  try {
    const response = await axios.get(`${API_URL}/items/${id}`);
    setReached(response.data);
    // ...same as 5/react, just named `id` instead of `index`
}
```

**Difference:** the URL is still `/items/<something>` — only what that
something *means* changed. In 5/react it was "the 3rd item in the
array." Here it's "the row whose database ID is this number,"
regardless of where it currently sits in the list.

## Step 5 — Update

```jsx
function startEditing(id, currentValue) {
  setEditingId(id);
  setEditValue(currentValue);
}

async function saveEdit(id, method) {
  try {
    await axios({
      method: method, // "PUT" or "PATCH"
      url: `${API_URL}/items/${id}`,
      // ...identical body/logic to 5/react
    });
  } catch (err) { /* ... */ }
  setEditingId(null);
  await loadItems();
}
```

**Difference:** `setEditingIndex` → `setEditingId`, same as step 1 —
purely a rename to match what's actually being tracked.

## Step 6 — Delete

Identical logic to 5/react — `DELETE /items/${id}` instead of
`DELETE /items/${index}`. **This is where the real, visible difference
shows up when you actually use the app:** delete a row in 5/react and
every row after it shifts down one index. Delete a row here and every
other row keeps its `#id` exactly as it was — nothing renumbers.

## Step 7 — Rendering

```jsx
{items.map((item) =>
  editingId === item.id ? (
    <li key={item.id}>...</li>
  ) : (
    <li key={item.id}>...</li>
  ),
)}
```

**Difference:** `.map((item, index) => ...)` → `.map((item) => ...)` —
there's no need to pull `index` out of `.map()` at all anymore, since
every value the UI needs (`id`, `value`) already lives on `item`
itself. `key={index}` also becomes `key={item.id}` — React's `key`
should always be a stable identity, and a database ID is a better one
than a position that can shift.

Everything else — the form, the button layout, the error handling — is
copy-identical to [5/react](../../5/react/STEPS.md).
