from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")  # add this

def to_ist(dt: datetime) -> datetime:
    """Convert a UTC datetime to IST."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.UTC)
    return dt.astimezone(IST)
