from pydantic import BaseModel

class ChatSchema(BaseModel):
    message: str