from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import open_meteo
import Holt_Winters_in_use as hw

# Import the simple variables from database.py
from database import engine, SessionLocal, ClickLog, Base
from sqlalchemy import text

app = FastAPI()

# Create tables on startup manually using the engine and Base
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

#only allows requests from my website                 
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

@app.post("/forecast")
def forecast(request: ForecastRequest):
    try:
        past_data = open_meteo.get_past_data(request.latitude, request.longitude)
        forecast = hw.forecast_from_data(past_data)
        return forecast
    except Exception as e:
        return {"status": "error", "message": str(e)}

## Tests ###  
#------------ database --
@app.post("/log-click")
def log_click():
    # 1. Manually ask the factory for a new session (workspace)
    db = SessionLocal()
    try:
        # 2. Use the workspace to add a record
        new_log = ClickLog()
        db.add(new_log)
        # 3. Manually hit "Save"
        db.commit()
        return {"status": "success"}
    except Exception as e:
        # If something goes wrong, cancel the save
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        # 4. ALWAYS close the workspace manually
        db.close()

@app.get("/click-count")
def get_click_count():
    # 1. Open workspace
    db = SessionLocal()
    try:
        # 2. Do the query
        count = db.query(ClickLog).count()
        return {"count": count}
    finally:
        # 3. Close workspace
        db.close()

@app.get("/db-test")
def test_db_connection():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Database connection successful!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
#------------ database --

@app.get("/")
def read_root():
    return {"Hello": "World!"}

class TestRequest(BaseModel):
    value: str

@app.post("/test")
def test(request: TestRequest):
    return {"value": request.value}

## Tests ###  

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
