import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { cart } = useCart();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <header className="navbar">
      <div className="container nav-inner">
        <Link to="/" className="brand">🛒 FreshCart</Link>
        <nav className="nav-links">
          <NavLink to="/" end>Shop</NavLink>
          {user && <NavLink to="/orders">My Orders</NavLink>}
          {user?.is_admin && <NavLink to="/admin">Admin</NavLink>}
          {user ? (
            <>
              <NavLink to="/cart" className="cart-link">
                Cart {cart.item_count > 0 && <span className="badge">{cart.item_count}</span>}
              </NavLink>
              <span className="muted hide-sm">Hi, {user.name.split(" ")[0]}</span>
              <button className="btn btn-ghost" onClick={handleLogout}>Logout</button>
            </>
          ) : (
            <>
              <NavLink to="/login">Login</NavLink>
              <Link to="/register" className="btn btn-primary btn-sm">Sign up</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
