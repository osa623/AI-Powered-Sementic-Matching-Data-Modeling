from pydantic import BaseModel

class ItemCreate(BaseModel):
    id: str
    description: str
    category: str