from fastapi import APIRouter, Header, Depends
from typing import Annotated
from app.controller.AppController import appController
from fastapi import APIRouter, UploadFile, File
from typing import List
from app.schemas.response_schema import FinalOutput


router = APIRouter()

@router.get("/")
def get_action():
    return appController.get_app_info()

@router.post("/detect", response_model=FinalOutput)
async def detect(images: List[UploadFile] = File(...)):
    return await appController.detect_image(images)