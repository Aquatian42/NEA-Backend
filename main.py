from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import open_meteo
import Holt_Winters_in_use as hw
from database import db_manager, ClickLog
from sqlalchemy.orm import Session
from fastapi import Depends

app = FastAPI()

# Create tables on startup
@app.on_event("startup")
def startup_event():
    db_manager.create_all()

#only allows requests from my website
origins = [
    "https://nea.tomdinning.com",
    "http://localhost:8000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
@app.get("/")
def read_root():
    return {"Hello": "World!"}

class TestRequest(BaseModel):
    value: str

@app.post("/test")
def test(request: TestRequest):
    
    return {"value": request.value}


@app.get("/db-test")


def test_db_connection():


    if db_manager.test_connection():


        return {"status": "success", "message": "Database connection successful!"}


    else:


        return {"status": "error", "message": "Database connection failed"}





@app.post("/log-click")


def log_click(db: Session = Depends(db_manager.get_db)):


    new_log = ClickLog()


    db.add(new_log)


    db.commit()


    return {"status": "success"}





@app.get("/click-count")


def get_click_count(db: Session = Depends(db_manager.get_db)):


    count = db.query(ClickLog).count()


    return {"count": count}





## Tests ###




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)