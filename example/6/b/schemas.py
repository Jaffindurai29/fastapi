from pydantic import BaseModel


class ItemRequest(BaseModel):
    value: str
