from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    access_token: str
    token_type: str


# Used for both POST and PUT (PUT replaces the whole note).
# There is NO owner_id here: the client never chooses the owner.
class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(default="", max_length=5000)


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    owner_id: int
