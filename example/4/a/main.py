from fastapi import FastAPI, HTTPException

app = FastAPI()

# Seeded with two items so this is testable on its own, without needing
# a POST first — GET is meant to be read-only here.
data = ["first", "second"]


# Show all data.
@app.get("/items")
def list_items():
    return data


# Reach one specific item — found by its position in the array.
@app.get("/items/{item_index}")
def get_item(item_index: int):
    if item_index < 0 or item_index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"index": item_index, "value": data[item_index]}
