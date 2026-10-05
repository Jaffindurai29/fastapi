from pydantic import BaseModel, Field

from ids import encode_id
from models import ItemModel


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)


class ItemOut(BaseModel):
    id: str  # the PUBLIC id, never the database integer
    name: str
    price: float

    # Built explicitly instead of from_attributes: row.id is an int and
    # must be encoded first. One obvious place where that happens.
    @classmethod
    def from_row(cls, row: ItemModel) -> "ItemOut":
        return cls(id=encode_id(row.id), name=row.name, price=row.price)
