from fastapi import FastAPI, HTTPException

app = FastAPI()

data = ["first", "second"]

@app.get("/items")
def list_items():
    return data
    
# PUT replaces the item at this index entirely — the client must send
# the full value, even if only part of it actually changed.
@app.put("/items/{item_index}")
def replace_item(item_index: int, value: str):
    if item_index < 0 or item_index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    data[item_index] = value
    return {"index": item_index, "value": data[item_index]}
