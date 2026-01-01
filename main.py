from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    "httpsa://nea.tomdinning.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TestRequest(BaseModel):
    value: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/test")
def test(request: TestRequest):
    return {"value": request.value}
