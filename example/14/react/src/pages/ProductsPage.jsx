import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { errorText, money } from "../api";

// Customer shop: browse products, fill a cart, place an order.
export default function ProductsPage() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState({}); // { productId: quantity }
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [notice, setNotice] = useState(null); // { type: 'error' | 'ok', text }
  const [placing, setPlacing] = useState(false);

  function load() {
    api.get("/products").then((res) => setProducts(res.data));
  }

  useEffect(load, []);

  function setQty(product, qty) {
    const quantity = Math.max(0, Math.min(qty, product.stock));
    setCart((prev) => {
      const next = { ...prev, [product.id]: quantity };
      if (quantity === 0) delete next[product.id];
      return next;
    });
  }

  const cartItems = products
    .filter((p) => cart[p.id])
    .map((p) => ({ product: p, quantity: cart[p.id] }));
  // Shown only as a preview. The backend works out the real total.
  const cartTotal = cartItems.reduce((sum, i) => sum + Number(i.product.price) * i.quantity, 0);

  async function placeOrder(e) {
    e.preventDefault();
    setPlacing(true);
    setNotice(null);
    try {
      await api.post("/orders", {
        items: cartItems.map((i) => ({ product_id: i.product.id, quantity: i.quantity })),
        phone,
        address,
      });
      setCart({});
      navigate("/orders");
    } catch (err) {
      // e.g. "Only 1 of Mug left" when someone else bought it first.
      setNotice({ type: "error", text: errorText(err) });
      load();
    } finally {
      setPlacing(false);
    }
  }

  return (
    <div className="shop">
      <section>
        <h2>Products</h2>
        {products.length === 0 && <p className="muted">No products yet.</p>}
        <div className="grid">
          {products.map((p) => (
            <div key={p.id} className="product">
              <h3>{p.name}</h3>
              {p.description && <p className="muted">{p.description}</p>}
              <div className="product-row">
                <strong>{money(p.price)}</strong>
                <span className={p.stock === 0 ? "stock out" : "stock"}>
                  {p.stock === 0 ? "Out of stock" : `${p.stock} in stock`}
                </span>
              </div>
              <div className="qty">
                <button
                  className="btn small secondary"
                  onClick={() => setQty(p, (cart[p.id] || 0) - 1)}
                  disabled={!cart[p.id]}
                >
                  −
                </button>
                <span>{cart[p.id] || 0}</span>
                <button
                  className="btn small"
                  onClick={() => setQty(p, (cart[p.id] || 0) + 1)}
                  disabled={(cart[p.id] || 0) >= p.stock}
                >
                  +
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      <aside className="panel">
        <h2>Cart</h2>
        {cartItems.length === 0 ? (
          <p className="muted">Your cart is empty.</p>
        ) : (
          <form onSubmit={placeOrder} className="stack">
            <ul className="lines">
              {cartItems.map(({ product, quantity }) => (
                <li key={product.id}>
                  <span>
                    {quantity} × {product.name}
                  </span>
                  <span>{money(Number(product.price) * quantity)}</span>
                </li>
              ))}
              <li className="total">
                <span>Total</span>
                <span>{money(cartTotal)}</span>
              </li>
            </ul>
            <label>
              Phone
              <input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                minLength={5}
                maxLength={30}
                required
              />
            </label>
            <label>
              Address
              <textarea
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                minLength={5}
                maxLength={300}
                rows={3}
                required
              />
            </label>
            <p className="hint">🔒 Phone and address are stored encrypted.</p>
            {notice && <div className={`alert ${notice.type}`}>{notice.text}</div>}
            <button className="btn" disabled={placing}>
              {placing ? "Placing…" : "Place order"}
            </button>
          </form>
        )}
      </aside>
    </div>
  );
}
