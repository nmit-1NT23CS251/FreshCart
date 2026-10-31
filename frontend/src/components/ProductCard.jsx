import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { errorMessage, rupees } from "../api";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

function StockBadge({ product }) {
  if (!product.in_stock) return <span className="stock stock-out">Out of stock</span>;
  if (product.low_stock) return <span className="stock stock-low">Only {product.stock} left</span>;
  return <span className="stock stock-ok">In stock</span>;
}

export default function ProductCard({ product }) {
  const { user } = useAuth();
  const { add, setQuantity, remove, quantityOf } = useCart();
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const inCart = quantityOf(product.id);

  const run = async (action) => {
    if (!user) return navigate("/login");
    setBusy(true);
    setError("");
    try {
      await action();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className={`card product ${product.in_stock ? "" : "is-out"}`}>
      <div className="product-emoji">{product.emoji}</div>
      <div className="product-body">
        <h3>{product.name}</h3>
        <p className="muted small">{product.unit}</p>
        <div className="product-row">
          <strong>{rupees(product.price)}</strong>
          <StockBadge product={product} />
        </div>
      </div>

      {inCart > 0 ? (
        <div className="stepper">
          <button disabled={busy} onClick={() => run(() => (inCart === 1 ? remove(product.id) : setQuantity(product.id, inCart - 1)))}>−</button>
          <span>{inCart}</span>
          <button disabled={busy || inCart >= product.stock} onClick={() => run(() => setQuantity(product.id, inCart + 1))}>+</button>
        </div>
      ) : (
        <button className="btn btn-primary btn-block" disabled={busy || !product.in_stock} onClick={() => run(() => add(product.id))}>
          {product.in_stock ? "Add to cart" : "Unavailable"}
        </button>
      )}
      {error && <p className="error small">{error}</p>}
    </div>
  );
}
