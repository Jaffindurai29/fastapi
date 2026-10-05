from pydantic import BaseModel, ConfigDict


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


# A cut-down item with NO category field. Used inside CategoryWithItems,
# where the category is already the outer object. If we reused ItemOut
# there, every item would repeat its category, which would list its
# items, which would repeat the category... forever.
class ItemSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float


# An item with its category nested inside, instead of category_id.
# from_attributes reads row.category (the relationship) and turns that
# CategoryModel into a CategoryOut.
class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    category: CategoryOut


# A category with its items nested inside (read from row.items).
class CategoryWithItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    items: list[ItemSummary]
