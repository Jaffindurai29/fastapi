from typing import Optional

from pydantic import BaseModel


class ItemPatch(BaseModel):
    value: Optional[str] = None
