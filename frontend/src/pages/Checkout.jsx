import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import api, { errorMessage, rupees } from "../api";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function Checkout() {
  const { user } = useAuth();
  const { cart, refresh } = useCart();
  const navigate = useNavigate();
  const [slots, setSlots] = useState([]);
  const [selected, setSelected] = useState(null);
  const [address, setAddress] = useState(user?.address || "");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.get("/slots").then((res) => setSlots(res.data)).catch((err) => setError(errorMessage(err)));
  }, []);

  if (cart.items.length === 0 && !busy) return <Navigate to="/cart" replace />;

  // Group slots by day: { "Today": [...], "Tomorrow": [...] }
  const days = slots.reduce((acc, s) => {
    (acc[s.label] ||= []).push(s);
    return acc;
  }, {});

  const placeOrder = async () => {
    setBusy(true);
    setError("");
    try {
      const res = await api.post("/orders", {
        slot_date: selected.date,
        slot_time: selected.time,
        address,
      });
      await refresh(); // cart is now empty
      navigate("/orders", { state: { placed: res.data.id } });
    } catch (err) {
      setError(errorMessage(err));
      api.get("/slots").then((r) => setSlots(r.data)).catch(() => {});
      setBusy(false);
    }
  };

  return (
    <div className="two-col">
      <div className="card">
        <h2>1. Choose a delivery slot</h2>
        {slots.length === 0 && <p className="muted">Loading slots…</p>}
        {Object.entries(days).map(([label, daySlots]) => (
          <div key={label} className="slot-day">
            <h4>{label} <span className="muted small">{daySlots[0].date}</span></h4>
            <div className="slots">
              {daySlots.map((s) => {
                const isSelected = selected?.date === s.date && selected?.time === s.time;
                return (
                  <button
                    key={s.time}
                    disabled={!s.available}
                    className={`slot ${isSelected ? "selected" : ""}`}
                    onClick={() => setSelected(s)}
                  >
                    <strong>{s.time.replace("-", " – ")}</strong>
                    <span className="small">{s.available ? `${s.remaining} left` : "Full"}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}

        <h2 className="mt">2. Delivery address</h2>
        <textarea className="input" rows={3} value={address} onChange={(e) => setAddress(e.target.value)} placeholder="House no, street, area, city, pincode" />
      </div>

      <div className="card summary">
        <h3>Order summary</h3>
        {cart.items.map((i) => (
          <div key={i.product.id} className="row-between small">
            <span>{i.product.emoji} {i.product.name} × {i.quantity}</span>
            <span>{rupees(i.subtotal)}</span>
          </div>
        ))}
        <hr />
        <div className="row-between total"><span>Total</span><span>{rupees(cart.total)}</span></div>
        {selected && <p className="small ok">Delivery: {selected.label}, {selected.time}</p>}
        {error && <p className="alert alert-error">{error}</p>}
        <button
          className="btn btn-primary btn-block"
          disabled={busy || !selected || address.trim().length < 5}
          onClick={placeOrder}
        >
          {busy ? "Placing order…" : "Place order (Cash on delivery)"}
        </button>
        {!selected && <p className="muted small center">Pick a slot to continue</p>}
      </div>
    </div>
  );
}
