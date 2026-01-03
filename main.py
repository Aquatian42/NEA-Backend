from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import open_meteo
import Holt_Winters_in_use as hw
from database import db, Users # Import the real DB manager and Users model
from utils import hash_password, verify_password
from sqlalchemy import text

app = FastAPI()

@app.on_event("startup")
def startup_event():
    dbtest.create_tables()
    db.create_tables()

# CORS Setup
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

class ForecastRequest(BaseModel):
    longitude: float
    latitude: float

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

# --- AUTH ROUTES ---

@app.post("/signup")
def signup(request: SignupRequest):
    with db.session() as s:
        # 1. Check if user exists
        existing_user = s.query(Users).filter(Users.username == request.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # 2. Hash password and save
        hashed = hash_password(request.password)
        new_user = Users(
            username=request.username,
            email=request.email,
            password_hash=hashed
        )
        s.add(new_user)
        # s.commit() is handled by our context manager 'with'
    return {"status": "success", "message": "User created"}

@app.post("/login")
def login(request: LoginRequest):
    with db.session() as s:
        # 1. Find user
        user = s.query(Users).filter(Users.username == request.username).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # 2. Verify password
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        return {
            "status": "success", 
            "message": "Logged in",
            "user": {"id": user.userID, "username": user.username}
        }

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