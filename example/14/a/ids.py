from typing import Annotated

from fastapi import HTTPException
from pydantic import PlainSerializer
from sqids import Sqids

from config import SQIDS_ALPHABET, SQIDS_MIN_LENGTH

# Database ids (1, 2, 3...) become short public ids ("Xb3kLq9P") in the
# API, and back again.
#
# Why: /orders/1, /orders/2... tells anyone how many orders the shop has
# and invites guessing. This is NOT security. What actually protects an
# order is the ownership check in routers/orders.py.
sqids = Sqids(alphabet=SQIDS_ALPHABET, min_length=SQIDS_MIN_LENGTH)


def encode_id(n: int) -> str:
    return sqids.encode([n])


def decode_id(public_id: str) -> int:
    """Public id -> database id. Anything we'd never hand out is a 404."""
    numbers = sqids.decode(public_id)
    # sqids can decode several strings to the same number. Only accept the
    # one string encode_id would produce, so every row has ONE valid id.
    if len(numbers) != 1 or encode_id(numbers[0]) != public_id:
        raise HTTPException(status_code=404, detail="Not found")
    return numbers[0]


# For response schemas: reads the int from the database row, writes the
# public string in the JSON.
PublicId = Annotated[int, PlainSerializer(encode_id, return_type=str)]
