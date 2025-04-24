from fastapi import FastAPI
from routes.api_routes import api_router

app = FastAPI(title="Medicine Detector")

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Medicine Image Detector API"}
