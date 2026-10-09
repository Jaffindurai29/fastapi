import { useEffect, useState } from "react";
import api, { errorText } from "../api";
import OrderCard from "../components/OrderCard";

// Same rules as NEXT_STATUS in backend/routers/orders.py. The backend
// enforces them; this only decides which buttons to show.
const NEXT_STATUS = {
  pending: ["shipped", "cancelled"],
  shipped: ["delivered"],
  delivered: [],
  cancelled: [],
};

export default function AdminOrdersPage() {
  const [orders, setOrders] = useState(null);
  const [notice, setNotice] = useState(null);

  function load() {
    api.get("/orders").then((res) => setOrders(res.data));
  }

  useEffect(load, []);

  async function setStatus(order, status) {
    setNotice(null);
    try {
      await api.patch(`/orders/${order.id}/status`, { status });
      load();
    } catch (err) {
      setNotice({ type: "error", text: errorText(err) });
    }
  }

  if (orders === null) return <p className="muted">Loading…</p>;

  return (
    <section>
      <h2>All orders</h2>
      <p className="hint">
        🔓 Phone and address are decrypted for you; in MySQL they're unreadable.
      </p>
      {notice && <div className={`alert ${notice.type}`}>{notice.text}</div>}
      {orders.length === 0 && <p className="muted">No orders yet.</p>}
      {orders.map((order) => (
        <OrderCard
          key={order.id}
          order={order}
          showCustomer
          actions={NEXT_STATUS[order.status].map((status) => (
            <button
              key={status}
              className={status === "cancelled" ? "btn small danger" : "btn small"}
              onClick={() => setStatus(order, status)}
            >
              Mark {status}
            </button>
          ))}
        />
      ))}
    </section>
  );
}
