from fastapi import UploadFile, File, HTTPException
from typing import List
from PIL import Image, UnidentifiedImageError
from io import BytesIO

from config.setting import env
from app.controller.PipelineController import pipelineController  # <- Fix importnya!

class AppController:
    def __init__(self):
        self.llm = None  # Optional: bisa dihapus kalau nggak dipakai
        # self.llm = ChatGoogleGenerativeAI(
        #     model="gemini-2.0-flash",
        #     google_api_key=env.google_api_key,
        # )

    def get_app_info(self):
        return {
            "app_name": env.app_name,
            "app_version": env.app_version,
        }
    
    async def detect_image(self, images: List[UploadFile] = File(...)):
        if not images:
            raise HTTPException(
                status_code=400,
                detail="No image files uploaded. Please upload at least one image."
            )

        pil_images = []
        try:
            for image_file in images:
                contents = await image_file.read()
                image = Image.open(BytesIO(contents))
                pil_images.append(image)
        except UnidentifiedImageError:
            raise HTTPException(
                status_code=400,
                detail="One or more uploaded files are not valid image files or not supported formats."
            )
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="An error occurred while processing the images."
            )

        result = pipelineController.run_pipeline(pil_images)
        return result

# === Tambahkan ini! ===
appController = AppController()
