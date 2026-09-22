from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# The React dev server (Vite) runs on a different origin/port than this
# API, so the browser needs explicit permission to read the response.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seeded with two items so the frontend has something to show on load.
data = ["first", "second"]


class ItemRequest(BaseModel):
    value: str


class ItemPatch(BaseModel):
    value: Optional[str] = None


@app.get("/items")
def list_items():
    return data


@app.get("/items/{item_index}")
def get_item(item_index: int):
    if item_index < 0 or item_index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"index": item_index, "value": data[item_index]}


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemRequest):
    data.append(item.value)
    return {"index": len(data) - 1, "value": item.value}


@app.put("/items/{item_index}")
def replace_item(item_index: int, item: ItemRequest):
    if item_index < 0 or item_index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    data[item_index] = item.value
    return {"index": item_index, "value": data[item_index]}


@app.patch("/items/{item_index}")
def update_item(item_index: int, patch: ItemPatch):
    if item_index < 0 or item_index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    if patch.value is not None:
        data[item_index] = patch.value
    return {"index": item_index, "value": data[item_index]}


@app.delete("/items/{item_index}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_index: int):
    if item_index < 0 or item_index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    data.pop(item_index)
