from pydantic import BaseModel
from typing import List, Optional

class PrimaryAgentOutput(BaseModel):
    is_anomaly: bool
    batch_and_expiry_image_index: Optional[List[int]] = []  # Default ke list kosong
    quantity_image_index: Optional[List[int]] = []  # Default ke list kosong
    item_name: Optional[str] = None  # Default ke None jika tidak ada item_name


class BatchNumberOutput(BaseModel):
    batch_number : str
    expiry_date : str

class QuantityOutput(BaseModel):
    quantity : int

class ItemMatch(BaseModel):
    item_name: Optional[str] = None
    item_code: Optional[str] = None