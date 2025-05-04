from config.setting import env
from app.utils.HttpResponseUtils import response_success
from fastapi import UploadFile, File, HTTPException
from typing import List
from PIL import Image
import io
from langchain.callbacks import tracing_v2_enabled
from app.controller.PipelineController_Lab import run_pipeline
from app.controller.PipelineController_Lab_Agent import run_pipeline_agent
from config import resources
from dotenv import load_dotenv
load_dotenv()
import os

class AppController:
    def __init__(self):
        self.llm = resources.llm
        self.llm_rag = resources.llm_rag
        self.embedding_model = resources.embedding_model
        self.client = resources.client
        pass

    def get_app_info(self):
        return response_success(
            data={
                "status" : "Server is running"
            }
        )
            

    async def process_images(self, images: List[UploadFile] = File(...)):
        if not images or len(images) == 0:
            raise HTTPException(
                status_code=400,
                detail="No images uploaded. Please upload at least one image."
            )
        
        try:
            pil_images = []
            for image in images:
                content = await image.read()
                pil_image = Image.open(io.BytesIO(content)).convert("RGB")
                pil_images.append(pil_image)
            
            # # Tambahkan tracing di sini
            with tracing_v2_enabled(project_name=os.getenv("LANGSMITH_PROJECT")):
                result = run_pipeline(pil_images)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        
        
    async def process_images_agent_multi(self, images: List[UploadFile] = File(...)):
        if not images or len(images) == 0:
            raise HTTPException(
                status_code=400,
                detail="No images uploaded. Please upload at least one image."
            )
        
        try:
            pil_images = []
            for image in images:
                content = await image.read()
                pil_image = Image.open(io.BytesIO(content)).convert("RGB")
                pil_images.append(pil_image)
            
            # # Tambahkan tracing di sini
            with tracing_v2_enabled(project_name=os.getenv("LANGSMITH_PROJECT")):
                result = run_pipeline_agent(pil_images)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    

appController = AppController()