from fastapi import FastAPI, UploadFile, File
from router.api import router
import os

# Debug: cek apakah GOOGLE_API_KEY sudah terbaca
print("[DEBUG] GOOGLE_API_KEY Loaded:", os.getenv("GOOGLE_API_KEY") is not None)


app = FastAPI(title="Obat Detector API")

# Tambahkan router endpoint dari router/api.py
app.include_router(router)

@app.get("/")
def root():
    return {
        "message": "Obat Detector API is running 🚀",
        "endpoints": {
            "analyze": {
                "path": "/analyze",
                "method": "POST",
                "description": "Upload images for detection (via multipart/form)"
            },
            "docs": "/docs"
        }
    }
