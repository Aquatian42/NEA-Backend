from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import open_meteo
import Holt_Winters_in_use as hw
from testdatabase import db, ClickLog
from sqlalchemy import text

app = FastAPI()

@app.on_event("startup")
def startup_event():
    db.create_tables()

# CORS Setup
origins = [
    "https://nea.tomdinning.com",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ForecastRequest(BaseModel):
    longitude: float
    latitude: float

# --- CLEAN DATABASE ROUTES ---

@app.post("/log-click")
def log_click():
    # needs with db.session() as s - code inside runs and once finished, functtion in database.py after yeild resumes
    with db.session() as s:
        new_log = ClickLog()
        s.add(new_log)
    return {"status": "success"}

@app.get("/click-count")
def get_click_count():
    # needs with db.session() as s - code inside runs and once finished, functtion in database.py after yeild resumes
    with db.session() as s:
        count = s.query(ClickLog).count()
        return {"count": count}

# --- OTHER ROUTES ---

@app.post("/forecast")
def forecast(request: ForecastRequest):
    try:
        past_data = open_meteo.get_past_data(request.latitude, request.longitude)
        forecast = hw.forecast_from_data(past_data)
        return forecast
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def read_root():
    return {"Hello": "World!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)