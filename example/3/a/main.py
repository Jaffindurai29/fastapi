from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# A Pydantic model describes the shape of the JSON body a POST request
# should send — two required fields here, both plain types.
class Item(BaseModel):
    name: str
    price: float


@app.post("/items")
def create_item(item: Item):
    # FastAPI already parsed and validated the JSON body into `item`
    # before this function ran. Returning it sends it straight back.
    return item
