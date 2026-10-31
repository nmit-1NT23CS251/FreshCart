# FreshCart 🛒

**FreshCart** is a full-stack grocery ordering web application with live inventory, shopping carts, scheduled delivery slots, and an admin dashboard for managing products and orders.

> **Project status:** Tested locally for customer and admin workflows. Not deployed yet.

## Features

### Customer
- Browse groceries by category, search for items, and filter for in-stock products.
- View live stock indicators and add products to a cart with stock validation.
- Select an available delivery slot and place a **cash-on-delivery** order.
- Track orders through fulfilment and cancel an order while it is pending.

### Admin
- View dashboard figures for revenue, orders, customers, and low-stock products.
- Add products, update stock, and remove products.
- Filter orders and update statuses: **Pending → Packed → Out for delivery → Delivered**.
- Cancel pending or packed orders and restore stock automatically.

## Tech stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 19, Vite, React Router, Axios |
| Backend | Python, FastAPI, Uvicorn |
| Database | SQLite, SQLAlchemy 2 |
| Authentication | JWT (PyJWT), bcrypt |
| Validation | Pydantic |

## Project structure

```text
grocery-app/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── ...
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   └── ...
│   └── package.json
├── HANDOVER.md
└── README.md
```

## Getting started

**Prerequisites:** Python 3, Node.js and npm.

### 1. Run the backend

From the project root:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend API: http://localhost:8000  
Interactive API docs: http://localhost:8000/docs

### 2. Run the frontend

Open a **second terminal** from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## Demo accounts

A demo admin is seeded on the first run. For a **local-only demo**, use:

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@grocery.com` | `admin123` |
| Customer | Sign up in the app | Password of your choice (min. 6 characters) |

**Security note:** These are sample development credentials. Change the admin password and configure a strong `SECRET_KEY` before deploying or exposing the app online.

## Delivery scheduling and inventory

- Three delivery windows each day: **08:00–10:00, 12:00–14:00, 18:00–20:00** (Asia/Kolkata).
- Slots are offered for today and the next two days, subject to capacity and booking cutoff.
- Checkout checks stock and uses a database transaction to avoid overselling; failed stock updates are rolled back.
- Cancelling an eligible order restores product stock.

## Configuration

| Environment variable | Purpose | Local default |
| --- | --- | --- |
| `DATABASE_URL` | Database connection | `sqlite:///./grocery.db` |
| `SECRET_KEY` | JWT signing secret | Development placeholder; **replace before deployment** |
| `VITE_API_URL` | Frontend API base URL | `http://localhost:8000` |

The backend also needs its CORS origins updated when the frontend is deployed.

## Current limitations and possible improvements

The current version supports cash on delivery only, uses emoji product icons, and runs locally. Future improvements could include online payments, PostgreSQL deployment, database migrations with Alembic, order notifications, automated tests, and product photos.

## Project documentation


## Author

Taqia Bakhtiar  
Computer Science Engineering — Nitte Meenakshi Institute of Technology, Bengaluru
