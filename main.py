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

class addLocationRequest(BaseModel):
    userID: int
    longitude: float
    latitude: float
    address: str

@app.post("/addLocation")
def addLocation(request: addLocationRequest):
    try:
        with db.session() as s:
            # SQLAlchemy filters use commas for 'and'
            existing_location = s.query(UserLocations).filter(
                UserLocations.longitude == request.longitude, 
                UserLocations.latitude == request.latitude,
                UserLocations.userID == request.userID
            ).first()
            if existing_location:
                return {"status": "info", "message": "Already saved"}

            new_location = UserLocations(
                userID=request.userID, 
                longitude=request.longitude, 
                latitude=request.latitude,
                address=request.address
            )
            s.add(new_location)
        return {"status": "success"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- ADMIN ROUTES ---

@app.get("/admin/log/{table_name}")
def admin_log_table(table_name: str):
    valid_tables = ["users", "UserData", "UserLocations"]
    if table_name not in valid_tables:
        raise HTTPException(status_code=400, detail="Invalid table name")
    
    with db.session() as s:
        # Use double quotes for table name to handle capital letters in Postgres
        result = s.execute(text(f'SELECT * FROM "{table_name}"'))
        # Convert rows to dictionaries for JSON response
        rows = [dict(row._mapping) for row in result]
        return rows

@app.post("/admin/clear/{table_name}")
def admin_clear_table(table_name: str):
    valid_tables = ["users", "UserData", "UserLocations"]
    if table_name not in valid_tables:
        raise HTTPException(status_code=400, detail="Invalid table name")
    
    with db.session() as s:
        s.execute(text(f'DELETE FROM "{table_name}"'))
        return {"status": "success", "message": f"Table {table_name} cleared"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)