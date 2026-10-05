from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# What the client sends. supplier_cost goes IN...
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    quantity: int = Field(default=0, ge=0)
    supplier_cost: float = Field(default=0, ge=0)


# ...but never comes back OUT. response_model=ItemOut drops every field
# that isn't listed here, even if the route returns the full database row.
class ItemOut(BaseModel):
    # Lets Pydantic read attributes off a SQLAlchemy object (row.name),
    # not just keys out of a dict (row["name"]).
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    quantity: int
    created_at: datetime
