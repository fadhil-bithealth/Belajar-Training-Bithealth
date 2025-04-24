from fastapi import APIRouter, UploadFile, File
from core.langgraph_flow import build_graph
from utils.image_loader import prepare_images

router = APIRouter()

graph = build_graph()

@router.post("/analyze")
async def analyze_obat(images: list[UploadFile] = File(...)):
    input_images = await prepare_images(images)
    result = graph.invoke({"images": input_images})
    return result
