from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from dependencies import get_db

# No prefix: this router's only route lives at /health.
router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        # The cheapest query there is. If it works, the database is up
        # and the connection settings are right.
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        # 503 Service Unavailable — the app is running, but can't do its job.
        return JSONResponse(status_code=503, content={"status": "error", "database": "unreachable"})
    return {"status": "ok", "database": "ok"}
