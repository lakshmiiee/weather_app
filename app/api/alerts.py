from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from app.core.database import get_db
from app.models.alert import WeatherAlert, WeatherAlertHistory
from app.schemas.alert_schema import AlertCreate
from app.models.weather import WeatherSnapshot
from app.utils.timezone import to_ist  # use the single shared function

router = APIRouter(prefix="/alerts", tags=["Alerts"])

# ------------------- POST /alerts -------------------
@router.post("/")
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    new_alert = WeatherAlert(
        city=alert.city,
        condition_type=alert.condition_type,
        operator=alert.operator,
        threshold_value=alert.threshold_value,
        active=alert.active,
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert

# ------------------- GET /alerts/{alert_id}/history -------------------
@router.get("/{alert_id}/history")
def get_alert_history(
    alert_id: int = Path(..., description="ID of the alert"),
    db: Session = Depends(get_db)
):
    alert = db.query(WeatherAlert).filter(WeatherAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    history = (
        db.query(WeatherAlertHistory)
        .filter(WeatherAlertHistory.alert_id == alert_id)
        .order_by(WeatherAlertHistory.triggered_at.desc())
        .all()
    )

    result = []
    for h in history:
        snapshot = db.query(WeatherSnapshot).filter(WeatherSnapshot.id == h.weather_snapshot_id).first()
        result.append({
            "triggered_at": h.triggered_at.isoformat(),
            "weather_snapshot": {
                "temperature": snapshot.temperature,
                "humidity": snapshot.humidity,
                "weather_condition": snapshot.weather_condition,
                "fetched_at": snapshot.fetched_at.isoformat()
            }
        })

    return {
        "alert_id": alert.id,
        "city": alert.city,
        "condition_type": alert.condition_type,
        "operator": alert.operator,
        "threshold_value": alert.threshold_value,
        "history": result
    }
