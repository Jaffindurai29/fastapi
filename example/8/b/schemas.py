from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0, le=1_000_000)
    quantity: int = Field(default=0, ge=0)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if value == "":
            raise ValueError("name must not be blank")
        return value


# Same rules as ItemCreate, but every field is optional — PATCH only
# sends what changed.
class ItemPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    price: Optional[float] = Field(default=None, gt=0, le=1_000_000)
    quantity: Optional[int] = Field(default=None, ge=0)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if value == "":
            raise ValueError("name must not be blank")
        return value
