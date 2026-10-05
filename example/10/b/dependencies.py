import os
import secrets

from fastapi import Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud
from database import SessionLocal
from models import ItemModel


# 1. The dependency every route has used since topic 6.
#    Code before `yield` runs before the route; the yielded value is
#    what the route receives as `db`; `finally` runs after the response
#    is ready, even if the route raised an exception, so the session is
#    always closed and its connection goes back to the pool.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 2. A dependency that depends on another dependency.
#    item_id comes from the path (same name as {item_id}); db comes
#    from get_db. The route gets back a real row, or never runs at all.
def get_item_or_404(item_id: int, db: Session = Depends(get_db)) -> ItemModel:
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found")
    return row


# 3. A class as a dependency. FastAPI calls Pagination(skip=..., limit=...)
#    with values read from the query string, and the route receives the
#    instance. Query(...) validates them like any other parameter.
class Pagination:
    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="Rows to skip"),
        limit: int = Query(default=10, ge=1, le=100, description="Max rows to return"),
    ):
        self.skip = skip
        self.limit = limit


# 4. A guard. It returns nothing useful; its only job is to raise 401
#    before the route runs if the X-API-Key header is missing or wrong.
#    FastAPI turns the parameter name x_api_key into the header name
#    X-API-Key (underscores become hyphens, case doesn't matter).
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("API_KEY", "dev-api-key")
    # compare_digest takes the same time whether the first or the last
    # character is wrong, so the key can't be guessed by timing replies.
    if x_api_key is None or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key")
