// One shared axios instance: every request goes to the FastAPI backend
// and automatically carries the login token if there is one.
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Turns any backend error into a readable sentence for the UI
export function errorMessage(err) {
  const detail = err?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg.replace("Value error, ", "")).join(", ");
  if (!err?.response) return "Can't reach the server. Is the backend running on port 8000?";
  return "Something went wrong. Please try again.";
}

export const rupees = (n) => `₹${Number(n).toFixed(2).replace(/\.00$/, "")}`;

export default api;
