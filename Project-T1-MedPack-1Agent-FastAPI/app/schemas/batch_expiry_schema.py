from pydantic import BaseModel

class BatchExpiryResult(BaseModel):
    batch_number: str
    expiry_date: str
