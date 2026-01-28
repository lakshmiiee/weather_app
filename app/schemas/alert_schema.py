from pydantic import BaseModel

class AlertCreate(BaseModel):
    city: str
    condition_type: str      # temperature, humidity, weather_condition
    operator: str            # >, <, =
    threshold_value: str
    active: bool = True
