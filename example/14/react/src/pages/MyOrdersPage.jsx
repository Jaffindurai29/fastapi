import { useEffect, useState } from "react";
import api from "../api";
import OrderCard from "../components/OrderCard";

export default function MyOrdersPage() {
  const [orders, setOrders] = useState(null);

  function load() {
    api.get("/orders/mine").then((res) => setOrders(res.data));
  }

  useEffect(load, []);

  async function cancel(order) {
    await api.post(`/orders/${order.id}/cancel`);
    load();
  }

  if (orders === null) return <p className="muted">Loading…</p>;

  return (
    <section>
      <h2>My orders</h2>
      {orders.length === 0 && <p className="muted">You haven't ordered anything yet.</p>}
      {orders.map((order) => (
        <OrderCard
          key={order.id}
          order={order}
          showCustomer
          actions={
            order.status === "pending" && (
              <button className="btn small danger" onClick={() => cancel(order)}>
                Cancel order
              </button>
            )
          }
        />
      ))}
    </section>
  );
}
