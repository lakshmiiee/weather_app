from app.core.database import engine, Base
from app.models.weather import WeatherSnapshot
from app.models.alert import WeatherAlert, WeatherAlertHistory

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("All tables created successfully")
