from typing import Optional

from fastapi import FastAPI, HTTPException

app = FastAPI()

data = ["first", "second"]


@app.get("/items")
def list_items():
    return data


# PATCH merges into the existing value instead of replacing it outright
# — unlike PUT, which always overwrites the whole thing.
@app.patch("/items/{item_index}")
def update_item(item_index: int, value: Optional[str] = None):
    if item_index < 0 or item_index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    if value is not None:
        data[item_index] += value
    return {"index": item_index, "value": data[item_index]}
