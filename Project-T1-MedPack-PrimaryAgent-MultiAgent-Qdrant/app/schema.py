# app/schema.py

from typing import List, Optional
from pydantic import BaseModel # type: ignore

class AnomalyResult(BaseModel):
    is_anomaly: bool
    
class DetectionResult(BaseModel):
    batch_and_expiry_image: List[int]
    quantity_detection_images: List[int]
    item_name: str

class BatchAndExpiryResult(BaseModel):
    batch_number: str
    expiry_date: str

class QuantityResult(BaseModel):
    quantity: int

class FinalOutput(BaseModel):
    item_id: Optional[str] = None  # <-- Tambahkan ini
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[str] = None
    #is_anomaly: Optional[bool] = False


class ItemMatch(BaseModel):
    item_name: Optional[str] = None
    item_code: Optional[str] = None


class PrimaryAgentResult(BaseModel):
    batch_and_expiry_image: List[int]
    quantity_detection_images: List[int]
    item_name: str
    is_anomaly: bool
