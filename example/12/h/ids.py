from sqids import Sqids

from config import SQIDS_ALPHABET, SQIDS_MIN_LENGTH

sqids = Sqids(alphabet=SQIDS_ALPHABET, min_length=SQIDS_MIN_LENGTH)


def encode_id(n: int) -> str:
    """Database id (int) -> public id (str), e.g. 1 -> 'igPHZLIU'."""
    return sqids.encode([n])


def decode_id(public_id: str) -> int | None:
    """Public id -> database id, or None if it isn't one we'd ever hand out."""
    numbers = sqids.decode(public_id)  # [] for characters not in the alphabet
    if len(numbers) != 1:  # garbage, or several numbers packed into one id
        return None
    # sqids can decode several different strings to the same number. Only
    # accept the one string encode_id would produce, so every row has
    # exactly ONE valid public id.
    if encode_id(numbers[0]) != public_id:
        return None
    return numbers[0]
