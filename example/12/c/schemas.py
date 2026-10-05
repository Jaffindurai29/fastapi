from pydantic import BaseModel, ConfigDict


# The OAuth2 spec fixes these two field names, and /docs relies on them.
class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_active: bool
