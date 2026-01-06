from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import open_meteo
import Holt_Winters_in_use as hw
from database import db, Users, UserData, UserLocations
from utils import hash_password, verify_password
from sqlalchemy import text
import requests

app = FastAPI()



@app.on_event("startup")
def startup_event():
    db.create_tables()

# only allow my website access
origins = [
    "https://nea.tomdinning.com",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#load api key from render environment
PLACES_API_KEY = os.environ.get("PLACES_API_KEY")

@app.post("/autocomplete")
def proxy_autocomplete(request: dict):
    url = "https://places.googleapis.com/v1/places:autocomplete"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": PLACES_API_KEY
    }
    response = requests.post(url, json=request, headers=headers)
    return response.json()

@app.get("/geocode/{place_id}")
def proxy_geocode(place_id: str):
    url = f"https://geocode.googleapis.com/v4beta/geocode/places/{place_id}?key={PLACES_API_KEY}"
    response = requests.get(url)
    return response.json()


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


@app.post("/signup")
def signup(request: SignupRequest):
    with db.session() as s:
        #check user exists
        existing_user = s.query(Users).filter(Users.username == request.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        hashed = hash_password(request.password)
        new_user = Users(username=request.username, email=request.email,password_hash=hashed)
        s.add(new_user)
        # s.commit() is handled by our context manager 'with'
    return {"status": "success", "message": "User created"}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(request: LoginRequest):
    with db.session() as s:
        user = s.query(Users).filter(Users.username == request.username).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        return {"status": "success", "message": "Logged in", "user": {"id": user.userID, "username": user.username}}

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

@app.get("/recent-locations/{user_id}")
def get_recent_locations(user_id: int):
    with db.session() as s:
        # Get last 5 locations for this user, ordered by locationID descending
        locations = s.query(UserLocations).filter(UserLocations.userID == user_id).order_by(UserLocations.locationID.desc()).limit(5).all()
        
        # Convert to list of dicts
        return [
            {
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "address": loc.address
            } for loc in locations
        ]

class addLocationRequest(BaseModel):
    userId: str
    longitude: float
    latitude: float
    address: str

@app.post("/addLocation")
def addLocation(request: addLocationRequest):
    try:
        with db.session() as s:
            new_location = UserLocations(
                userID=int(request.userId), 
                longitude=request.longitude, 
                latitude=request.latitude,
                address=request.address
            )
            s.add(new_location)
        return {"status": "success"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- testing ---
# allows fastapi to serve data from the specified paths
@app.get("/admin/log/{table_name}")
def admin_log_table(table_name: str):
    valid_tables = ["users", "userdata", "userlocations"]
    if table_name.lower() not in valid_tables:
        raise HTTPException(status_code=400, detail="Invalid table name")
    
    with db.session() as s:
        
        result = s.execute(text(f'SELECT * FROM "{table_name}"'))
        # Convert rows to dictionaries for JSON response
        rows = [dict(row._mapping) for row in result]
        return rows

@app.post("/admin/clear/{table_name}")
def admin_clear_table(table_name: str):
    valid_tables = ["users", "userdata", "userlocations"]
    if table_name.lower() not in valid_tables:
        raise HTTPException(status_code=400, detail="Invalid table name")
    
    with db.session() as s:
        s.execute(text(f'DELETE FROM "{table_name}"'))
        return {"status": "success", "message": f"Table {table_name} cleared"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)