from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.alert import WeatherAlert, WeatherAlertHistory
from app.models.weather import WeatherSnapshot

IST = ZoneInfo("Asia/Kolkata")


def evaluate_alerts(snapshot: WeatherSnapshot, db: Session):
    # Get all active alerts for the city
    alerts = (
        db.query(WeatherAlert)
        .filter(
            WeatherAlert.city == snapshot.city,
            WeatherAlert.active.is_(True),
        )
        .all()
    )

    for alert in alerts:
        triggered = False
        value = None

        if alert.condition_type == "temperature":
            value = snapshot.temperature

        elif alert.condition_type == "humidity":
            value = snapshot.humidity

        elif alert.condition_type == "weather_condition":
            value = snapshot.weather_condition

        # Numeric conditions
        if alert.condition_type in ("temperature", "humidity"):
            threshold = float(alert.threshold_value)

            if alert.operator == ">" and value > threshold:
                triggered = True
            elif alert.operator == "<" and value < threshold:
                triggered = True
            elif alert.operator == "=" and value == threshold:
                triggered = True

        # String condition (weather)
        else:
            if (
                alert.operator == "="
                and value.lower() == alert.threshold_value.lower()
            ):
                triggered = True

        # Save alert history if triggered
        if triggered:
            history = WeatherAlertHistory(
                alert_id=alert.id,
                weather_snapshot_id=snapshot.id,
                triggered_at=datetime.now(IST),  # ✅ IST time
            )
            db.add(history)
            db.commit()
