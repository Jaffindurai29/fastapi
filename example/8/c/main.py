import logging

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

import crud
from database import Base, SessionLocal, engine, get_db
from exceptions import AppError
from schemas import ItemCreate, ItemPatch

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()
logger = logging.getLogger("uvicorn.error")


# Every error this API returns has the same shape:
#   {"error": {"code": "...", "message": "...", "fields": [...]}}
# so a frontend only needs one piece of code to display any of them.
def error_response(status_code: int, code: str, message: str, fields=None):
    body = {"error": {"code": code, "message": message}}
    if fields:
        body["error"]["fields"] = fields
    return JSONResponse(status_code=status_code, content=body)


# 1. Our own business errors (ItemNotFound, DuplicateItemName, ...).
@app.exception_handler(AppError)
def handle_app_error(request: Request, exc: AppError):
    return error_response(exc.status_code, exc.code, exc.message)


# 2. Pydantic validation failures — replaces FastAPI's default 422 body.
@app.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError):
    fields = [
        {"field": ".".join(str(part) for part in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return error_response(
        422, "validation_error", "Invalid request", fields
    )


# 3. Errors raised by FastAPI/Starlette itself — unknown URL (404),
#    wrong method (405), or any HTTPException a route still raises.
@app.exception_handler(StarletteHTTPException)
def handle_http_error(request: Request, exc: StarletteHTTPException):
    return error_response(exc.status_code, f"http_{exc.status_code}", str(exc.detail))


# 4. Anything unexpected. Log the real error, but never send the stack
#    trace (or database details) to the client.
@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
    return error_response(500, "internal_error", "Something went wrong")


# The routes have no error handling at all now — crud.py raises, and
# the handlers above turn it into a response.
@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    return [{"id": r.id, "name": r.name, "price": r.price, "quantity": r.quantity} for r in crud.get_items(db)]


@app.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_item(db, item_id)
    return {"id": row.id, "name": row.name, "price": row.price, "quantity": row.quantity}


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    row = crud.create_item(db, item)
    return {"id": row.id, "name": row.name, "price": row.price, "quantity": row.quantity}


@app.patch("/items/{item_id}")
def update_item(item_id: int, patch: ItemPatch, db: Session = Depends(get_db)):
    row = crud.update_item(db, item_id, patch)
    return {"id": row.id, "name": row.name, "price": row.price, "quantity": row.quantity}


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    crud.delete_item(db, item_id)


# A deliberately broken route, to see handler 4 in action.
@app.get("/boom")
def boom():
    return 1 / 0
