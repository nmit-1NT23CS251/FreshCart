import { useEffect, useState } from "react";
import api, { errorMessage, rupees } from "../api";
import { StatusBadge, statusLabel } from "./Orders";

const NEXT_STATUS = { PENDING: "PACKED", PACKED: "OUT_FOR_DELIVERY", OUT_FOR_DELIVERY: "DELIVERED" };
const FILTERS = ["", "PENDING", "PACKED", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"];
const EMPTY_PRODUCT = { name: "", category: "", price: "", unit: "", stock: "", emoji: "🛒" };

function Stats({ stats }) {
  if (!stats) return null;
  return (
    <div className="stats">
      <div className="card stat"><span className="muted small">Revenue</span><strong>{rupees(stats.revenue)}</strong></div>
      <div className="card stat"><span className="muted small">Orders</span><strong>{stats.total_orders}</strong></div>
      <div className="card stat"><span className="muted small">Pending</span><strong>{stats.orders_by_status.PENDING || 0}</strong></div>
      <div className="card stat"><span className="muted small">Customers</span><strong>{stats.customers}</strong></div>
      <div className="card stat"><span className="muted small">Low / out of stock</span><strong>{stats.low_stock.length}</strong></div>
    </div>
  );
}

function OrdersTab({ onChange }) {
  const [orders, setOrders] = useState([]);
  const [filter, setFilter] = useState("");
  const [error, setError] = useState("");

  const load = () =>
    api.get("/admin/orders", { params: { status: filter || undefined } })
      .then((res) => setOrders(res.data))
      .catch((err) => setError(errorMessage(err)));

  useEffect(() => {
    load();
  }, [filter]);

  const changeStatus = async (id, status) => {
    setError("");
    try {
      await api.patch(`/admin/orders/${id}/status`, { status });
      load();
      onChange();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  return (
    <>
      <div className="chips">
        {FILTERS.map((f) => (
          <button key={f} className={`chip ${filter === f ? "active" : ""}`} onClick={() => setFilter(f)}>
            {f ? statusLabel(f) : "All"}
          </button>
        ))}
      </div>
      {error && <p className="alert alert-error">{error}</p>}
      {orders.length === 0 ? <p className="muted center">No orders here.</p> : (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr><th>#</th><th>Customer</th><th>Slot</th><th>Items</th><th>Total</th><th>Status</th><th>Action</th></tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id}>
                  <td>{o.id}</td>
                  <td>{o.user.name}<div className="muted small">{o.address}</div></td>
                  <td className="nowrap">{o.slot_date}<div className="muted small">{o.slot_time}</div></td>
                  <td className="small">{o.items.map((i) => `${i.product_name} × ${i.quantity}`).join(", ")}</td>
                  <td>{rupees(o.total)}</td>
                  <td><StatusBadge status={o.status} /></td>
                  <td className="actions">
                    {NEXT_STATUS[o.status] && (
                      <button className="btn btn-primary btn-sm" onClick={() => changeStatus(o.id, NEXT_STATUS[o.status])}>
                        Mark {statusLabel(NEXT_STATUS[o.status]).toLowerCase()}
                      </button>
                    )}
                    {["PENDING", "PACKED"].includes(o.status) && (
                      <button className="btn btn-ghost btn-sm" onClick={() => changeStatus(o.id, "CANCELLED")}>Cancel</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function ProductsTab({ onChange }) {
  const [products, setProducts] = useState([]);
  const [stockEdits, setStockEdits] = useState({});
  const [form, setForm] = useState(EMPTY_PRODUCT);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const load = () => api.get("/products").then((res) => setProducts(res.data));

  useEffect(() => {
    load();
  }, []);

  const wrap = async (action, success) => {
    setError("");
    setMessage("");
    try {
      await action();
      await load();
      onChange();
      setMessage(success);
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const saveStock = (p) =>
    wrap(async () => {
      await api.patch(`/products/${p.id}/stock`, { stock: Number(stockEdits[p.id]) });
      setStockEdits(({ [p.id]: _, ...rest }) => rest);
    }, `Stock updated for ${p.name}`);

  const addProduct = (e) => {
    e.preventDefault();
    wrap(async () => {
      await api.post("/products", { ...form, price: Number(form.price), stock: Number(form.stock) });
      setForm(EMPTY_PRODUCT);
    }, `${form.name} added`);
  };

  const deleteProduct = (p) => {
    if (window.confirm(`Delete ${p.name}?`)) wrap(() => api.delete(`/products/${p.id}`), `${p.name} deleted`);
  };

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  return (
    <>
      <form className="card add-product" onSubmit={addProduct}>
        <h3>Add a product</h3>
        <div className="form-grid">
          <input className="input" placeholder="Emoji" value={form.emoji} onChange={update("emoji")} maxLength={4} />
          <input className="input" placeholder="Name" required value={form.name} onChange={update("name")} />
          <input className="input" placeholder="Category" required value={form.category} onChange={update("category")} />
          <input className="input" placeholder="Unit (e.g. 1 kg)" required value={form.unit} onChange={update("unit")} />
          <input className="input" placeholder="Price ₹" type="number" min="1" step="0.5" required value={form.price} onChange={update("price")} />
          <input className="input" placeholder="Stock" type="number" min="0" required value={form.stock} onChange={update("stock")} />
          <button className="btn btn-primary">Add</button>
        </div>
      </form>

      {error && <p className="alert alert-error">{error}</p>}
      {message && <p className="alert alert-success">{message}</p>}

      <div className="card table-wrap">
        <table>
          <thead><tr><th></th><th>Product</th><th>Category</th><th>Price</th><th>Stock</th><th></th></tr></thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id} className={p.stock === 0 ? "row-out" : p.low_stock ? "row-low" : ""}>
                <td className="cart-emoji">{p.emoji}</td>
                <td>{p.name}<div className="muted small">{p.unit}</div></td>
                <td>{p.category}</td>
                <td>{rupees(p.price)}</td>
                <td>
                  <div className="stock-edit">
                    <input
                      className="input input-sm"
                      type="number"
                      min="0"
                      value={stockEdits[p.id] ?? p.stock}
                      onChange={(e) => setStockEdits({ ...stockEdits, [p.id]: e.target.value })}
                    />
                    {stockEdits[p.id] !== undefined && String(stockEdits[p.id]) !== String(p.stock) && (
                      <button className="btn btn-primary btn-sm" onClick={() => saveStock(p)}>Save</button>
                    )}
                  </div>
                </td>
                <td><button className="icon-btn" title="Delete" onClick={() => deleteProduct(p)}>🗑</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default function Admin() {
  const [tab, setTab] = useState("orders");
  const [stats, setStats] = useState(null);

  const loadStats = () => api.get("/admin/stats").then((res) => setStats(res.data)).catch(() => {});

  useEffect(() => {
    loadStats();
  }, []);

  return (
    <>
      <h2>Admin dashboard</h2>
      <Stats stats={stats} />
      <div className="tabs">
        <button className={tab === "orders" ? "active" : ""} onClick={() => setTab("orders")}>Orders</button>
        <button className={tab === "products" ? "active" : ""} onClick={() => setTab("products")}>Products & stock</button>
      </div>
      {tab === "orders" ? <OrdersTab onChange={loadStats} /> : <ProductsTab onChange={loadStats} />}
    </>
  );
}
