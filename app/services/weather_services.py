# app/services/weather_services.py

import httpx
from fastapi import HTTPException
from datetime import datetime
from zoneinfo import ZoneInfo
import pytz

OPENWEATHER_API_KEY = "d7c3575b4d5824813f700c840b12b84e"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


IST = pytz.timezone("Asia/Kolkata")


def ist_now():
    return datetime.now(IST)



async def fetch_weather_from_api(city: str):
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(
                OPENWEATHER_URL,
                params={
                    "q": city,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric",
                },
            )
            response.raise_for_status()

        except httpx.HTTPStatusError:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text,
            )

        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))

    data = response.json()

    # OpenWeather `dt` is UTC → convert to IST
    fetched_at = datetime.fromtimestamp(data.get("dt"), tz=ZoneInfo("UTC")).astimezone(IST)

    return {
        "city": data.get("name"),
        "temperature": data.get("main", {}).get("temp"),
        "humidity": data.get("main", {}).get("humidity"),
        "weather_condition": data.get("weather", [{}])[0].get("main"),
        "fetched_at": fetched_at,
        "source": "OpenWeather",
    }
