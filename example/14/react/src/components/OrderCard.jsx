import { money } from "../api";

// One order, used by both "My orders" and the admin "Orders" page.
// `actions` is whatever buttons the page wants to show for it.
export default function OrderCard({ order, showCustomer, actions }) {
  return (
    <div className="order">
      <div className="order-head">
        <div>
          <strong>Order #{order.id}</strong>
          <span className="muted"> · {new Date(order.created_at).toLocaleString()}</span>
        </div>
        <span className={`badge status-${order.status}`}>{order.status}</span>
      </div>

      {showCustomer && (
        <p className="muted">
          {order.username} · {order.phone} · {order.address}
        </p>
      )}

      <ul className="lines">
        {order.items.map((item) => (
          <li key={item.product_id}>
            <span>
              {item.quantity} × {item.product_name}
            </span>
            <span>{money(Number(item.unit_price) * item.quantity)}</span>
          </li>
        ))}
        <li className="total">
          <span>Total</span>
          <span>{money(order.total)}</span>
        </li>
      </ul>

      {actions && <div className="order-actions">{actions}</div>}
    </div>
  );
}
