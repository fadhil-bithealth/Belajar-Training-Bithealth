
from pydantic import BaseModel
from typing import List

class ImageUploadRequest(BaseModel):
    filenames: List[str]

class ImageUploadResponse(BaseModel):
    message: str
