from fastapi import FastAPI

app = FastAPI()

data = ["first", "second"]

@app.get("/items")
def list_items():
    return data

# Add a new item to the end of the array.
@app.post("/items")
def create_item(value: str):
    data.append(value)
    return {"index": len(data) - 1, "value": value}
