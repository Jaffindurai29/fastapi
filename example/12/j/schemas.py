from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    # max_length stops someone sending a 10 MB "password" to burn CPU
    # in the hasher.
    password: str = Field(min_length=8, max_length=128)
    # No "role" field on purpose: a client must never be able to make
    # itself an admin by sending {"role": "admin"}. Extra keys are ignored.


# CHECKLIST: response_model never exposes hashed_password. It simply
# isn't listed here, so it can't leave the server even by accident.
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(default="", max_length=2000)


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    owner_id: int
