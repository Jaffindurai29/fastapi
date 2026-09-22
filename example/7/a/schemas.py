from typing import Optional

from pydantic import BaseModel


class ItemRequest(BaseModel):
    value: str


class ItemPatch(BaseModel):
    value: Optional[str] = None
