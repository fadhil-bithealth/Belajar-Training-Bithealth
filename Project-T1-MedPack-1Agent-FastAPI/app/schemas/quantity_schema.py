from pydantic import BaseModel

class QuantityResult(BaseModel):
    item_quantity: int
