from typing import List, Optional
from pydantic import BaseModel

class AnomalyResult(BaseModel):
    is_anomaly: bool

class DetectionResult(BaseModel):
    batch_and_expiry_image: List[int]
    quantity_detection_images: List[int]
    item_name: str

class FinalOutput(BaseModel):
    item_name: str
    batch_number: str
    expiry_date: str
    item_quantity: int
