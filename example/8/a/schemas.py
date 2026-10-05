from pydantic import BaseModel, Field, field_validator


class ItemCreate(BaseModel):
    # Field(...) adds rules on top of the type. If any rule fails, FastAPI
    # answers 422 before your route function even runs.
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0, le=1_000_000)
    quantity: int = Field(default=0, ge=0)

    # A rule Field() can't express: "   " passes min_length=1, but it's
    # still blank. Raising ValueError here becomes a 422 too.
    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if value == "":
            raise ValueError("name must not be blank")
        return value
