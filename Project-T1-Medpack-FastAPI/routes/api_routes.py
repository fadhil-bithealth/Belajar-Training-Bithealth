
from fastapi import APIRouter
from app.controllers import AppController

api_router = APIRouter()
api_router.include_router(AppController.router, tags=["Image Detection"])
