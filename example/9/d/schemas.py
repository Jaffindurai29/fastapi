from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    price: float
    created_at: datetime


# The envelope: one page of rows, plus what a frontend needs to draw
# "Page 2 of 3" and know whether a Next button makes sense.
class ItemPage(BaseModel):
    items: list[ItemOut]
    total: int  # rows matching the filters, across ALL pages
    page: int
    size: int
    pages: int  # ceil(total / size)
