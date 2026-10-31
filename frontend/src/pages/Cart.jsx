import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { errorMessage, rupees } from "../api";
import { useCart } from "../context/CartContext";

export default function Cart() {
  const { cart, refresh, setQuantity, remove, clear } = useCart();
  const navigate = useNavigate();
  const [error, setError] = useState("");

  // Re-check live stock every time the cart page opens
  useEffect(() => {
    refresh().catch(() => {});
  }, [refresh]);

  const run = async (action) => {
    setError("");
    try {
      await action();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const problems = cart.items.filter((i) => i.quantity > i.product.stock);

  if (cart.items.length === 0) {
    return (
      <div className="card empty">
        <div className="big-emoji">🧺</div>
        <h2>Your cart is empty</h2>
        <Link to="/" className="btn btn-primary">Start shopping</Link>
      </div>
    );
  }

  return (
    <div className="two-col">
      <div className="card">
        <div className="row-between">
          <h2>Your cart</h2>
          <button className="btn btn-ghost" onClick={() => run(clear)}>Clear cart</button>
        </div>
        {error && <p className="alert alert-error">{error}</p>}
        {cart.items.map(({ product, quantity, subtotal }) => (
          <div key={product.id} className="cart-row">
            <span className="cart-emoji">{product.emoji}</span>
            <div className="grow">
              <strong>{product.name}</strong>
              <p className="muted small">{product.unit} · {rupees(product.price)} each</p>
              {quantity > product.stock && (
                <p className="error small">
                  {product.stock === 0 ? "Now out of stock — please remove it" : `Only ${product.stock} available now`}
                </p>
              )}
            </div>
            <div className="stepper">
              <button onClick={() => run(() => (quantity === 1 ? remove(product.id) : setQuantity(product.id, quantity - 1)))}>−</button>
              <span>{quantity}</span>
              <button disabled={quantity >= product.stock} onClick={() => run(() => setQuantity(product.id, quantity + 1))}>+</button>
            </div>
            <strong className="price">{rupees(subtotal)}</strong>
            <button className="icon-btn" title="Remove" onClick={() => run(() => remove(product.id))}>✕</button>
          </div>
        ))}
      </div>

      <div className="card summary">
        <h3>Summary</h3>
        <div className="row-between"><span>Items</span><span>{cart.item_count}</span></div>
        <div className="row-between"><span>Delivery</span><span className="ok">Free</span></div>
        <hr />
        <div className="row-between total"><span>Total</span><span>{rupees(cart.total)}</span></div>
        {problems.length > 0 && <p className="alert alert-error small">Fix the stock issues above before checkout.</p>}
        <button className="btn btn-primary btn-block" disabled={problems.length > 0} onClick={() => navigate("/checkout")}>
          Choose delivery slot →
        </button>
      </div>
    </div>
  );
}
