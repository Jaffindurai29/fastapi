from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    price: float
    created_at: datetime


# The same filters as GET /items, gathered into one model. Field(...)
# takes the same rules (ge, le, min_length, description) as Query(...).
class FilterParams(BaseModel):
    # Unknown query parameters (a typo like ?limt=5) become a 422
    # instead of being silently ignored.
    model_config = {"extra": "forbid"}

    search: str | None = Field(
        None, min_length=2, max_length=50, description="Case-insensitive 'name contains'"
    )
    category: list[str] | None = Field(None, description="Repeat to match several categories")
    min_price: float | None = Field(None, ge=0, description="Lowest price, inclusive")
    max_price: float | None = Field(None, ge=0, description="Highest price, inclusive")
    sort_by: Literal["id", "name", "price", "created_at"] = "id"
    order: Literal["asc", "desc"] = "asc"
    skip: int = Field(0, ge=0, description="Rows to skip")
    limit: int = Field(10, ge=1, le=100, description="Rows to return (max 100)")
