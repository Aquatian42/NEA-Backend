from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import open_meteo

app = FastAPI()

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
def forecast(forecast: ForecastRequest):
    return openmeteo.get_past_data(ForecastRequest.latitude, ForecastRequest.longitude)


### Tests ###
# @app.get("/")
# def read_root():
#     return {"Hello": "World!"}

# class TestRequest(BaseModel):
#     value: str

# @app.post("/test")
# def test(request: TestRequest):
#     return {"value": request.value}

### Tests ###

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)