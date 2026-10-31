import { createContext, useCallback, useContext, useEffect, useState } from "react";
import api from "../api";
import { useAuth } from "./AuthContext";

const EMPTY = { items: [], total: 0, item_count: 0 };
const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState(EMPTY);

  const refresh = useCallback(async () => {
    if (!user) return setCart(EMPTY);
    const res = await api.get("/cart");
    setCart(res.data);
  }, [user]);

  // Reload the cart whenever the logged-in user changes
  useEffect(() => {
    refresh().catch(() => setCart(EMPTY));
  }, [refresh]);

  // Every action returns the updated cart from the backend
  const add = async (productId, quantity = 1) =>
    setCart((await api.post("/cart/items", { product_id: productId, quantity })).data);
  const setQuantity = async (productId, quantity) =>
    setCart((await api.put(`/cart/items/${productId}`, { quantity })).data);
  const remove = async (productId) => setCart((await api.delete(`/cart/items/${productId}`)).data);
  const clear = async () => setCart((await api.delete("/cart")).data);

  const quantityOf = (productId) =>
    cart.items.find((i) => i.product.id === productId)?.quantity || 0;

  return (
    <CartContext.Provider value={{ cart, refresh, add, setQuantity, remove, clear, quantityOf }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
