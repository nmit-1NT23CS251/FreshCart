import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import api, { errorMessage, rupees } from "../api";

export const STEPS = ["PENDING", "PACKED", "OUT_FOR_DELIVERY", "DELIVERED"];
export const statusLabel = (s) => s.replaceAll("_", " ").toLowerCase().replace(/^\w/, (c) => c.toUpperCase());

export function StatusBadge({ status }) {
  return <span className={`status status-${status.toLowerCase()}`}>{statusLabel(status)}</span>;
}

function Progress({ status }) {
  if (status === "CANCELLED") return null;
  const current = STEPS.indexOf(status);
  return (
    <div className="progress">
      {STEPS.map((step, i) => (
        <div key={step} className={`step ${i <= current ? "done" : ""}`}>
          <span className="dot" />
          <span className="small">{statusLabel(step)}</span>
        </div>
      ))}
    </div>
  );
}

export default function Orders() {
  const location = useLocation();
  const [orders, setOrders] = useState(null);
  const [error, setError] = useState("");

  const load = () =>
    api.get("/orders").then((res) => setOrders(res.data)).catch((err) => setError(errorMessage(err)));

  useEffect(() => {
    load();
  }, []);

  const cancel = async (id) => {
    if (!window.confirm("Cancel this order?")) return;
    try {
      await api.post(`/orders/${id}/cancel`);
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  if (orders === null) return <p className="muted center">Loading orders…</p>;

  return (
    <>
      <h2>My orders</h2>
      {location.state?.placed && (
        <p className="alert alert-success">🎉 Order #{location.state.placed} placed! We'll deliver it in your chosen slot.</p>
      )}
      {error && <p className="alert alert-error">{error}</p>}
      {orders.length === 0 && (
        <div className="card empty">
          <p>You haven't placed any orders yet.</p>
          <Link to="/" className="btn btn-primary">Shop now</Link>
        </div>
      )}
      {orders.map((o) => (
        <div key={o.id} className="card order">
          <div className="row-between">
            <div>
              <strong>Order #{o.id}</strong>
              <p className="muted small">Placed {new Date(o.created_at).toLocaleString()}</p>
            </div>
            <StatusBadge status={o.status} />
          </div>
          <Progress status={o.status} />
          <p className="small">🚚 Delivery slot: <strong>{o.slot_date}, {o.slot_time}</strong></p>
          <p className="small muted">📍 {o.address}</p>
          <ul className="order-items">
            {o.items.map((i) => (
              <li key={i.product_id} className="row-between small">
                <span>{i.product_name} × {i.quantity}</span>
                <span>{rupees(i.price_at_purchase * i.quantity)}</span>
              </li>
            ))}
          </ul>
          <div className="row-between">
            <strong>Total: {rupees(o.total)}</strong>
            {o.status === "PENDING" && <button className="btn btn-danger btn-sm" onClick={() => cancel(o.id)}>Cancel order</button>}
          </div>
        </div>
      ))}
    </>
  );
}
