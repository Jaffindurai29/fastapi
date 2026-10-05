from pydantic import BaseModel, ConfigDict, Field


# What the client sends: plain values.
class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    phone: str = Field(min_length=3, max_length=30)
    notes: str | None = Field(default=None, max_length=2000)


# What the client gets back: decrypted values. The field names differ
# from the columns (phone vs phone_encrypted), so main.py builds this
# explicitly instead of using from_attributes.
class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    notes: str | None


# LEARNING ONLY: the row exactly as stored, ciphertext and all.
class CustomerRawOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone_encrypted: str
    notes_encrypted: str | None
