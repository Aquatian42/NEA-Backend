from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ForecastInput(BaseModel):
    value: str

@app.post("/forecast")
def get_forecast(data: ForecastInput):
    # For testing, just echo the input value in the response
    return {"prediction": f"Forecast for value: {data.value}"}