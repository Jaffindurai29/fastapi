import { useEffect, useState } from "react";
import api, { errorText } from "../api";

const EMPTY = { name: "", description: "", price: "", stock: "0" };

export default function AdminProductsPage() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [notice, setNotice] = useState(null);

  function load() {
    api.get("/products").then((res) => setProducts(res.data));
  }

  useEffect(load, []);

  // Runs an API call, then reloads the list (or shows why it failed).
  async function run(request) {
    setNotice(null);
    try {
      await request;
      load();
      return true;
    } catch (err) {
      setNotice({ type: "error", text: errorText(err) });
      return false;
    }
  }

  async function addProduct(e) {
    e.preventDefault();
    const ok = await run(api.post("/products", { ...form, stock: Number(form.stock) }));
    if (ok) setForm(EMPTY);
  }

  return (
    <section>
      <h2>Products</h2>

      <form className="panel add-form" onSubmit={addProduct}>
        <input
          placeholder="Name"
          value={form.name}
          required
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        <input
          placeholder="Description"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
        <input
          placeholder="Price"
          type="number"
          min="0.01"
          step="0.01"
          value={form.price}
          required
          onChange={(e) => setForm({ ...form, price: e.target.value })}
        />
        <input
          placeholder="Stock"
          type="number"
          min="0"
          value={form.stock}
          required
          onChange={(e) => setForm({ ...form, stock: e.target.value })}
        />
        <button className="btn">Add product</button>
      </form>

      {notice && <div className={`alert ${notice.type}`}>{notice.text}</div>}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Change stock</th>
              <th>Visible</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <ProductRow key={p.id} product={p} run={run} />
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ProductRow({ product, run }) {
  const [price, setPrice] = useState(product.price);
  const [change, setChange] = useState("");

  async function applyStock() {
    if (await run(api.patch(`/products/${product.id}/stock`, { change: Number(change) }))) {
      setChange("");
    }
  }

  return (
    <tr className={product.is_active ? "" : "hidden-row"}>
      <td>
        <strong>{product.name}</strong>
        <div className="muted small-text">id: {product.id}</div>
      </td>
      <td>
        <div className="inline">
          <input
            className="narrow"
            type="number"
            min="0.01"
            step="0.01"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
          />
          {Number(price) !== Number(product.price) && (
            <button
              className="btn small"
              onClick={() => run(api.patch(`/products/${product.id}`, { price }))}
            >
              Save
            </button>
          )}
        </div>
      </td>
      <td>
        <span className={product.stock === 0 ? "stock out" : "stock"}>{product.stock}</span>
      </td>
      <td>
        <div className="inline">
          <input
            className="narrow"
            type="number"
            placeholder="+5 / -2"
            value={change}
            onChange={(e) => setChange(e.target.value)}
          />
          <button className="btn small" disabled={!Number(change)} onClick={applyStock}>
            Apply
          </button>
        </div>
      </td>
      <td>
        {product.is_active ? (
          <button
            className="btn small secondary"
            onClick={() => run(api.delete(`/products/${product.id}`))}
          >
            Hide
          </button>
        ) : (
          <button
            className="btn small"
            onClick={() => run(api.patch(`/products/${product.id}`, { is_active: true }))}
          >
            Show
          </button>
        )}
      </td>
    </tr>
  );
}
