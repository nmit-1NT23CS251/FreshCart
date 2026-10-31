"""Entry point: creates the app and tables, adds sample data, and plugs in every router."""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas  # noqa: F401  (importing models registers all tables)
from .database import Base, SessionLocal, engine, get_db
from .routers import admin, auth, cart, orders, products
from .seed import seed_database
from .slots import generate_slots


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # create tables if they don't exist yet
    with SessionLocal() as db:
        seed_database(db)                   # add admin + sample products the first time
    yield


app = FastAPI(title="Grocery App API", lifespan=lifespan)

# Allows the React app (running on port 5173) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(admin.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.get("/slots", response_model=list[schemas.SlotOut], tags=["Delivery slots"])
def list_slots(db: Session = Depends(get_db)):
    return generate_slots(db)
