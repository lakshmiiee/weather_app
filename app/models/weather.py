from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.database import Base
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


def ist_now():
    return datetime.now(IST)


class WeatherSnapshot(Base):
    __tablename__ = "weather_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), index=True, nullable=False)

    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    weather_condition = Column(String(100), nullable=False)

    fetched_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=ist_now
    )

    source = Column(String(50), nullable=False)
