"""Delivery slot rules: which time windows exist, and which ones can still be booked."""
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models, schemas

TIMEZONE = ZoneInfo("Asia/Kolkata")
SLOT_TIMES = ["08:00-10:00", "12:00-14:00", "18:00-20:00"]
SLOT_CAPACITY = 5      # max orders per slot
DAYS_AHEAD = 3         # today + next 2 days
CUTOFF_HOURS = 1       # must book at least 1 hour before the slot starts


def now_local() -> datetime:
    return datetime.now(TIMEZONE).replace(tzinfo=None)


def generate_slots(db: Session) -> list[schemas.SlotOut]:
    now = now_local()
    slots = []
    for day_offset in range(DAYS_AHEAD):
        day = (now + timedelta(days=day_offset)).date()
        for window in SLOT_TIMES:
            start = datetime.combine(day, time(int(window[:2])))
            if start - timedelta(hours=CUTOFF_HOURS) <= now:
                continue  # too late to book this slot
            booked = db.scalar(
                select(func.count(models.Order.id)).where(
                    models.Order.slot_date == day.isoformat(),
                    models.Order.slot_time == window,
                    models.Order.status != "CANCELLED",
                )
            )
            remaining = max(SLOT_CAPACITY - booked, 0)
            if day_offset == 0:
                label = "Today"
            elif day_offset == 1:
                label = "Tomorrow"
            else:
                label = day.strftime("%a, %d %b")
            slots.append(
                schemas.SlotOut(
                    date=day.isoformat(), label=label, time=window,
                    available=remaining > 0, remaining=remaining,
                )
            )
    return slots


def is_slot_bookable(db: Session, slot_date: str, slot_time: str) -> bool:
    return any(
        s.date == slot_date and s.time == slot_time and s.available
        for s in generate_slots(db)
    )
