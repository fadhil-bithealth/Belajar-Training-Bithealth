from fastapi import APIRouter
import app.schemas as schemas
from app.controller.AppController import appController
from fastapi import UploadFile, File
from typing import List
from PIL import Image
from app.schemas import FinalOutput

router = APIRouter()

@router.get("/")
def get_action():
    return appController.get_app_info()

@router.post("/echo")
def post_echo_action(user: schemas.UserSchema):
    return appController.echo_data(user)

@router.post("/detect/", response_model=FinalOutput)
async def process_images(images: List[UploadFile] = File(...)):
    # Make sure you await the process_images method
    result = await appController.process_images(images)  # Corrected here
    return result

@router.post("/detect_using_1_agent/", response_model=FinalOutput)
async def process_images(images: List[UploadFile] = File(...)):
    # Make sure you await the process_images method
    result = await appController.process_images_agent_multi(images)  # Corrected here
    return result