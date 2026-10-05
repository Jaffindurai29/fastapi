from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=30)


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    category_id: int
    # Optional: tag the item while creating it. Defaults to no tags.
    tag_ids: list[int] = []


# No tags field here: used inside a tag's item list, where the tag is
# already known (same reason as ItemSummary in 11/b).
class ItemSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    category_id: int
    tags: list[TagOut]
