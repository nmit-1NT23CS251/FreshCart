# FreshCart: Grocery Ordering App

Customers browse daily essentials, check live availability, add items to a cart,
and schedule delivery in a time slot. Admins manage stock and move orders through
fulfilment (Pending → Packed → Out for delivery → Delivered).

**Stack:** FastAPI + SQLAlchemy + SQLite (backend), React + Vite + Axios (frontend), JWT auth.

## Run it

**Terminal 1: backend**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

**Terminal 2: frontend**
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:5173

Admin login: `admin@grocery.com` / `admin123` (created automatically with 26 sample products).
To start fresh, stop the backend and delete `backend/grocery.db`.

## Features
- Browse by category, search, "in stock only" filter, live stock badges
- Cart with stock checks on every change
- Delivery slots: 3 windows a day for 3 days, max 5 orders per slot, 1-hour booking cutoff
- Checkout reduces stock atomically in one transaction (no overselling if two people buy the last item)
- Order tracking with status progress; customers can cancel pending orders (stock is restored)
- Admin dashboard: revenue and order stats, order status updates, add/delete products, edit stock

## Project structure
```
backend/app/
  main.py        app setup, CORS, table creation, /health, /slots
  database.py    engine, session, get_db
  models.py      User, Product, CartItem, Order, OrderItem
  schemas.py     Pydantic request/response models
  auth.py        bcrypt hashing, JWT, get_current_user, require_admin
  slots.py       delivery slot rules
  seed.py        admin account + sample products
  routers/       auth, products, cart, orders, admin
frontend/src/
  api.js         axios instance with JWT interceptor
  context/       AuthContext, CartContext
  components/    Navbar, ProductCard, ProtectedRoute
  pages/         Home, Login, Register, Cart, Checkout, Orders, Admin
```

## API overview
| Method | Route | Who |
|---|---|---|
| POST | /auth/register, /auth/login | anyone |
| GET | /products, /products/categories, /products/{id}, /products/{id}/availability | anyone |
| GET | /slots | anyone |
| GET/POST/PUT/DELETE | /cart, /cart/items, /cart/items/{product_id} | customer |
| POST/GET | /orders, /orders/{id}, /orders/{id}/cancel | customer |
| POST/PUT/PATCH/DELETE | /products, /products/{id}, /products/{id}/stock | admin |
| GET/PATCH | /admin/orders, /admin/orders/{id}/status, /admin/stats | admin |
