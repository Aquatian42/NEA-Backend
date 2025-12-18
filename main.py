from fastapi import FastAPI

app = FastAPI()

@app.get("/forecast")
def health():
    return {"status": "Ok! This is working hoow!"}