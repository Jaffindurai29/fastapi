from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ItemOut(BaseModel):
    # Read attributes off the SQLAlchemy row (see 8/d).
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    price: float
    created_at: datetime
