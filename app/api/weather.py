# app/api/weather.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.core.database import get_db
from app.models.weather import WeatherSnapshot
from app.services.weather_services import fetch_weather_from_api
from app.utils.timezone import to_ist, IST

router = APIRouter(prefix="/weather", tags=["Weather"])

# ------------------- GET /weather -------------------
@router.get("/")
async def get_weather(city: str, db: Session = Depends(get_db)):
    if not city:
        raise HTTPException(status_code=400, detail="City name is required")

    # Ensure ten_minutes_ago is timezone-aware UTC
    ten_minutes_ago_utc = datetime.now(timezone.utc) - timedelta(minutes=10)

    snapshot = (
        db.query(WeatherSnapshot)
        .filter(WeatherSnapshot.city == city)
        .order_by(WeatherSnapshot.fetched_at.desc())
        .first()
    )

    # Return cached IST data if fresh
    if snapshot and snapshot.fetched_at:
        # Ensure snapshot.fetched_at is timezone-aware
        fetched_at_utc = (
            snapshot.fetched_at
            if snapshot.fetched_at.tzinfo is not None
            else snapshot.fetched_at.replace(tzinfo=timezone.utc)
        )

        if fetched_at_utc > ten_minutes_ago_utc:
            return {
                "city": snapshot.city,
                "temperature": snapshot.temperature,
                "humidity": snapshot.humidity,
                "weather_condition": snapshot.weather_condition,
                "fetched_at": to_ist(fetched_at_utc).isoformat(),
                "source": snapshot.source,
            }

    # Fetch fresh data from API (already IST)
    data = await fetch_weather_from_api(city)

    new_snapshot = WeatherSnapshot(
        city=city,
        temperature=data["temperature"],
        humidity=data["humidity"],
        weather_condition=data["weather_condition"],
        source=data["source"],
        fetched_at=data["fetched_at"],  # should be aware datetime from service
    )

    db.add(new_snapshot)
    db.commit()
    db.refresh(new_snapshot)

    # Trigger alerts
    from app.services.alert_engine import evaluate_alerts
    evaluate_alerts(new_snapshot, db)

    return {
        "city": new_snapshot.city,
        "temperature": new_snapshot.temperature,
        "humidity": new_snapshot.humidity,
        "weather_condition": new_snapshot.weather_condition,
        "fetched_at": to_ist(new_snapshot.fetched_at).isoformat(),
        "source": new_snapshot.source,
    }

# ------------------- GET /weather/history -------------------
@router.get("/history")
def get_weather_history(
    city: str = Query(...),
    from_date: str = Query(...),
    to_date: str = Query(...),
    limit: int = Query(50),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    from app.utils.timezone import IST

    try:
        from_dt = to_ist(datetime.fromisoformat(from_date))
        to_dt = to_ist(datetime.fromisoformat(to_date) + timedelta(days=1) - timedelta(seconds=1))

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format YYYY-MM-DD")

    snapshots = (
        db.query(WeatherSnapshot)
        .filter(
            WeatherSnapshot.city == city,
            WeatherSnapshot.fetched_at >= from_dt,
            WeatherSnapshot.fetched_at <= to_dt,
        )
        .order_by(WeatherSnapshot.fetched_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "city": city,
        "from": from_date,
        "to": to_date,
        "count": len(snapshots),
        "data": [
            {
                "city": s.city,
                "temperature": s.temperature,
                "humidity": s.humidity,
                "weather_condition": s.weather_condition,
                "fetched_at": to_ist(
                    s.fetched_at if s.fetched_at.tzinfo else s.fetched_at.replace(tzinfo=timezone.utc)
                ).isoformat(),
                "source": s.source,
            }
            for s in snapshots
        ],
    }
