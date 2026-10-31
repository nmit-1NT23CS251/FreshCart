import { useEffect, useState } from "react";
import api, { errorMessage } from "../api";
import ProductCard from "../components/ProductCard";

export default function Home() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [inStockOnly, setInStockOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/products/categories").then((res) => setCategories(res.data)).catch(() => {});
  }, []);

  // Re-fetch whenever a filter changes (search waits 300 ms after typing stops)
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(true);
      api
        .get("/products", { params: { category: category || undefined, search: search || undefined, in_stock_only: inStockOnly } })
        .then((res) => {
          setProducts(res.data);
          setError("");
        })
        .catch((err) => setError(errorMessage(err)))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [category, search, inStockOnly]);

  return (
    <>
      <section className="hero">
        <h1>Daily essentials, delivered on your schedule</h1>
        <p>Browse fresh groceries, check what's in stock, and pick a delivery slot that suits you.</p>
      </section>

      <div className="filters">
        <input
          className="input search"
          placeholder="Search milk, rice, bread…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <label className="checkbox">
          <input type="checkbox" checked={inStockOnly} onChange={(e) => setInStockOnly(e.target.checked)} />
          In stock only
        </label>
      </div>

      <div className="chips">
        <button className={`chip ${category === "" ? "active" : ""}`} onClick={() => setCategory("")}>All</button>
        {categories.map((c) => (
          <button key={c} className={`chip ${category === c ? "active" : ""}`} onClick={() => setCategory(c)}>{c}</button>
        ))}
      </div>

      {error && <p className="alert alert-error">{error}</p>}
      {loading && products.length === 0 ? (
        <p className="muted center">Loading products…</p>
      ) : products.length === 0 ? (
        <p className="muted center">No products match your filters.</p>
      ) : (
        <div className="grid">
          {products.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </>
  );
}
