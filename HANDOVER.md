# FreshCart: Project Handover

**Project:** FreshCart, a grocery ordering app with live stock and scheduled delivery slots
**Owner:** Taqia Bakhtiar (CSE, NMIT Bangalore)
**Date:** 31 October 2026
**Status:** Working end to end (customer flow + admin flow tested). Runs locally; not deployed yet.

---

## 1. What the app does

Customers browse daily essentials, see live stock, add items to a cart, and choose a delivery time slot.
The store admin manages stock and moves each order through fulfilment.

| Customer | Admin |
|---|---|
| Browse by category, search, "in stock only" filter | Dashboard: revenue, orders, pending, customers, low stock |
| Live stock badges (In stock / Only N left / Out of stock) | View all orders, filter by status |
| Cart with stock checks on every change | Move orders: Pending → Packed → Out for delivery → Delivered |
| Pick a delivery slot (3 per day, 3 days ahead) | Cancel pending/packed orders (stock is restored) |
| Place order (cash on delivery) | Add products, edit stock, delete products |
| Track orders with a progress bar, cancel while Pending | |

---

## 2. Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, React Router, Axios |
| Backend | Python, FastAPI, Uvicorn |
| Database | SQLite via SQLAlchemy 2 (file: `backend/grocery.db`) |
| Auth | JWT tokens (PyJWT), passwords hashed with bcrypt |
| Validation | Pydantic |

---

## 3. How to run it (macOS)

Two terminals are needed: one for the backend, one for the frontend.

### Terminal 1: backend
```bash
cd ~/Documents/grocery-app/backend
source venv/bin/activate
pip install -r requirements.txt          # first time only
venv/bin/python -m uvicorn app.main:app --reload
```
Wait for **"Application startup complete"**.
API docs: http://localhost:8000/docs

> Always start the backend with `venv/bin/python -m uvicorn ...`.
> Plain `uvicorn ...` can pick up the Homebrew Python, which doesn't have the packages
> (error: `ModuleNotFoundError: No module named 'sqlalchemy'`).

### Terminal 2: frontend
```bash
cd ~/Documents/grocery-app/frontend
npm install                              # first time only
npm run dev
```
App: http://localhost:5173

### First-time setup on a new machine
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
If `npm run dev` fails with a native binding / rolldown error, run `rm -rf node_modules && npm install` in `frontend`.

### Logins
| Role | Email | Password |
|---|---|---|
| Admin | admin@grocery.com | admin123 |
| Customer | Register from the Sign up page | your choice (min 6 characters) |

On first start, the backend creates the tables, the admin account, and 26 sample products automatically.
**To reset all data:** stop the backend, delete `backend/grocery.db`, start it again.

---

## 4. Folder structure

```
grocery-app/
├── README.md
├── HANDOVER.md                  ← this file
├── .gitignore
├── backend/
│   ├── requirements.txt
│   ├── venv/                    (not in git)
│   ├── grocery.db               (created on first run, not in git)
│   └── app/
│       ├── main.py              app setup, CORS, startup (tables + seed), /health, /slots
│       ├── database.py          engine, session, get_db()
│       ├── models.py            database tables
│       ├── schemas.py           request / response shapes (Pydantic)
│       ├── auth.py              bcrypt, JWT, get_current_user, require_admin
│       ├── slots.py             delivery slot rules
│       ├── seed.py              admin account + sample products
│       └── routers/
│           ├── auth.py          /auth/*
│           ├── products.py      /products/*
│           ├── cart.py          /cart/*
│           ├── orders.py        /orders/*
│           └── admin.py         /admin/*
└── frontend/
    ├── index.html, package.json, vite.config.js
    └── src/
        ├── main.jsx             app entry, wraps providers
        ├── App.jsx              routes
        ├── api.js               axios instance (adds JWT), error + ₹ helpers
        ├── index.css            all styles
        ├── context/
        │   ├── AuthContext.jsx  logged-in user, login/register/logout
        │   └── CartContext.jsx  cart state + add/update/remove
        ├── components/
        │   ├── Navbar.jsx
        │   ├── ProductCard.jsx  stock badge, add / − + buttons
        │   └── ProtectedRoute.jsx  blocks logged-out users / non-admins
        └── pages/
            ├── Home.jsx         browse, search, filters
            ├── Login.jsx, Register.jsx
            ├── Cart.jsx
            ├── Checkout.jsx     slot picker + address
            ├── Orders.jsx       order history + tracking
            └── Admin.jsx        stats, orders tab, products & stock tab
```

---

## 5. Data model

| Table | Key columns | Notes |
|---|---|---|
| `users` | id, name, email (unique), hashed_password, address, is_admin | Address is saved from the first order if empty |
| `products` | id, name, category, price, unit, stock, emoji | `stock` is the live availability |
| `cart_items` | user_id → users, product_id → products, quantity | One row per user + product (unique) |
| `orders` | user_id, total, status, slot_date, slot_time, address, created_at | Status: PENDING, PACKED, OUT_FOR_DELIVERY, DELIVERED, CANCELLED |
| `order_items` | order_id → orders, product_id, product_name, quantity, price_at_purchase | Name and price are copied so old orders stay correct |

Relationships: a User has many Orders; an Order has many OrderItems; a CartItem points to one Product.

---

## 6. API reference

All protected routes need the header `Authorization: Bearer <token>` (the frontend adds it automatically).

| Method | Route | Access | Purpose |
|---|---|---|---|
| GET | `/health` | public | Server check |
| POST | `/auth/register` | public | Create account, returns token + user |
| POST | `/auth/login` | public | Log in, returns token + user |
| GET / PUT | `/auth/me` | logged in | View / update own name and address |
| GET | `/products?category=&search=&in_stock_only=` | public | List products |
| GET | `/products/categories` | public | List categories |
| GET | `/products/{id}` | public | One product |
| GET | `/products/{id}/availability?quantity=` | public | Can I buy N of this? |
| POST | `/products` | admin | Add product |
| PUT | `/products/{id}` | admin | Edit product |
| PATCH | `/products/{id}/stock` | admin | Set stock |
| DELETE | `/products/{id}` | admin | Delete product (also removes it from carts) |
| GET | `/slots` | public | Bookable delivery slots |
| GET / DELETE | `/cart` | logged in | View / clear cart |
| POST | `/cart/items` | logged in | Add product (adds to existing quantity) |
| PUT / DELETE | `/cart/items/{product_id}` | logged in | Set quantity / remove |
| POST | `/orders` | logged in | Place order from cart with slot + address |
| GET | `/orders`, `/orders/{id}` | logged in | My orders / one order |
| POST | `/orders/{id}/cancel` | logged in | Cancel own PENDING order |
| GET | `/admin/orders?status=` | admin | All orders |
| PATCH | `/admin/orders/{id}/status` | admin | Change order status |
| GET | `/admin/stats` | admin | Dashboard numbers |

Interactive docs with "Try it out": http://localhost:8000/docs (use the **Authorize** button with a token from `/auth/login`).

---

## 7. Business rules

**Stock**
- A product with stock 0 cannot be added to the cart.
- Cart quantity can never go above current stock.
- "Only N left" shows when stock is 1–5.

**Delivery slots** (`backend/app/slots.py`)
| Setting | Value |
|---|---|
| Windows | 08:00–10:00, 12:00–14:00, 18:00–20:00 |
| Days shown | Today + next 2 days |
| Capacity | 5 orders per slot (cancelled orders don't count) |
| Cutoff | A slot can't be booked less than 1 hour before it starts |
| Timezone | Asia/Kolkata |

**Placing an order** (`backend/app/routers/orders.py`)
1. Cart must not be empty and the slot must still be bookable.
2. For each item, stock is reduced with a conditional update: *reduce only where stock ≥ quantity*.
   If two people buy the last unit at the same time, only one succeeds (no overselling).
3. Everything runs in one transaction. If any item fails, all stock changes are rolled back and the user gets a 409 error.
4. On success: order saved, cart emptied, address remembered.

**Order status flow** (`backend/app/routers/admin.py`)
```
PENDING ──► PACKED ──► OUT_FOR_DELIVERY ──► DELIVERED
   │           │
   └──► CANCELLED ◄──┘
```
- Customers can cancel only PENDING orders. Admins can cancel PENDING or PACKED.
- Cancelling puts the stock back.
- Any other jump (e.g. PENDING → DELIVERED) is rejected with a 400 error.

---

## 8. Configuration

| Setting | Where | Default | Change before deploying? |
|---|---|---|---|
| `DATABASE_URL` | env var, read in `database.py` | `sqlite:///./grocery.db` | Yes, use PostgreSQL |
| `SECRET_KEY` | env var, read in `auth.py` | placeholder string | **Yes, must change** |
| Token expiry | `auth.py` → `TOKEN_EXPIRE_MINUTES` | 1 day | Optional |
| Allowed frontend origins (CORS) | `main.py` | localhost:5173 | Yes, add the deployed URL |
| API URL for frontend | env var `VITE_API_URL` | http://localhost:8000 | Yes |
| Admin login | `seed.py` | admin@grocery.com / admin123 | **Yes, change password** |
| Slot times, capacity, cutoff | `slots.py` | see section 7 | Optional |

---

## 9. Known limitations

- **Payments:** cash on delivery only; no payment gateway yet.
- **No database migrations:** if you change `models.py`, delete `grocery.db` to recreate tables (this wipes data). Use Alembic for real migrations.
- **Product images are emojis**, not uploaded photos.
- **Token is stored in localStorage**, which is fine for a demo; production apps often use httpOnly cookies.
- **Slot capacity check and order creation aren't locked together**, so under very heavy load a slot could take one extra order. Stock overselling *is* prevented.
- **No automated test suite in the repo** (the flows were tested manually and with a script).
- **No email/SMS notifications.**
- **Not deployed**; runs on localhost only.

---

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'sqlalchemy'` (or fastapi, jwt…) | Start with `venv/bin/python -m uvicorn app.main:app --reload` from the `backend` folder |
| Red underlines on imports in VS Code | Cmd+Shift+P → "Python: Select Interpreter" → Enter interpreter path → `./backend/venv/bin/python` |
| Frontend says "Can't reach the server" | Backend isn't running; start Terminal 1 |
| CORS error in browser console | Frontend must run on port 5173, or add its URL to `allow_origins` in `main.py` |
| `npm run dev` fails with a native binding error | `cd frontend && rm -rf node_modules && npm install` |
| Error about missing column / table after editing models | Stop backend, delete `backend/grocery.db`, restart |
| "This email is already registered" | Log in instead, or use a different email |
| No delivery slots showing | All of today's slots may be past the cutoff; tomorrow's should show. Check the system clock. |
| Logged in but cart/orders show "Please log in" | Token expired; log out and log in again |

---

## 11. Suggested next steps

1. **Payments:** add Razorpay (test mode) at checkout.
2. **Deploy:** backend on Render, frontend on Vercel, database on Neon / Render PostgreSQL. Set `SECRET_KEY`, `DATABASE_URL`, `VITE_API_URL`, and CORS origins.
3. **Migrations:** add Alembic so model changes don't wipe data.
4. **Notifications:** email or SMS when an order is out for delivery.
5. **Product images:** upload real photos (e.g. Cloudinary) instead of emojis.
6. **Tests:** add pytest tests for cart limits, checkout, overselling, and status changes.
7. **Smart reorder:** suggest items the user buys regularly.

---

## 12. Demo checklist (for presentations)

- [ ] Start backend, then frontend, then open http://localhost:5173
- [ ] Register a customer, add 3–4 items, place one order before presenting (so admin has data)
- [ ] Show: stock badges → add to cart → "+" beyond stock is blocked → choose slot → place order → My Orders progress bar
- [ ] Log in as admin → show stats → Mark packed → Products & stock → edit a stock number
- [ ] Optional: open http://localhost:8000/docs to show the auto-generated API docs
