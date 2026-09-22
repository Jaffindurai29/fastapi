from fastapi import FastAPI, HTTPException, status

app = FastAPI()

data = ["first", "second"]


@app.get("/items")
def list_items():
    return data


@app.delete("/items/{item_index}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_index: int):
    if item_index < 0 or item_index >= len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    data.pop(item_index)
