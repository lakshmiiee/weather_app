from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz
from app.core.database import Base

IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST)

class WeatherAlert(Base):
    __tablename__ = "weather_alerts"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False)
    condition_type = Column(String(50), nullable=False)
    operator = Column(String(5), nullable=False)
    threshold_value = Column(String(50), nullable=True)
    active = Column(Boolean, default=True)

    history = relationship(
        "WeatherAlertHistory",
        back_populates="alert",
        cascade="all, delete"
    )

class WeatherAlertHistory(Base):
    __tablename__ = "weather_alert_history"
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("weather_alerts.id"), nullable=False)
    weather_snapshot_id = Column(Integer, ForeignKey("weather_snapshots.id"), nullable=False)
    triggered_at = Column(DateTime(timezone=True), nullable=False, default=ist_now)

    alert = relationship("WeatherAlert", back_populates="history")
