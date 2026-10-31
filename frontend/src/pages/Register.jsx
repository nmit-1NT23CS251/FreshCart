import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { errorMessage } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", address: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await register({ ...form, address: form.address || null });
      navigate("/");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card auth-card">
      <h2>Create your account</h2>
      <form onSubmit={handleSubmit} className="form">
        <label>Full name<input className="input" required minLength={2} value={form.name} onChange={update("name")} /></label>
        <label>Email<input className="input" type="email" required value={form.email} onChange={update("email")} /></label>
        <label>Password<input className="input" type="password" required minLength={6} value={form.password} onChange={update("password")} /></label>
        <label>Delivery address <span className="muted">(optional)</span>
          <textarea className="input" rows={2} value={form.address} onChange={update("address")} />
        </label>
        {error && <p className="alert alert-error">{error}</p>}
        <button className="btn btn-primary btn-block" disabled={busy}>{busy ? "Creating…" : "Sign up"}</button>
      </form>
      <p className="muted small center">Already have an account? <Link to="/login">Log in</Link></p>
    </div>
  );
}
