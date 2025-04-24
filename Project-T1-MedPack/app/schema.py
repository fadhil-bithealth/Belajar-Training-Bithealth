# app/schema.py

from typing import List, Optional
from pydantic import BaseModel # type: ignore

class AnomalyResult(BaseModel):
    is_anomaly: bool
    
class DetectionResult(BaseModel):
    batch_and_expiry_image: List[int]
    quantity_detection_images: List[int]
    item_name: str

class FinalOutput(BaseModel):
    is_anomaly: bool
    batch_and_expiry_image: Optional[List[int]] = []
    quantity_detection_images: Optional[List[int]] = []
    item_name: Optional[str] = None
