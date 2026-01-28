from fastapi import FastAPI
from app.api import  weather, alerts


app = FastAPI(title="Weather Management & Alert System")



app.include_router(weather.router)  
app.include_router(alerts.router)

@app.get("/")
def root():
    return {"status": "API is running"}
