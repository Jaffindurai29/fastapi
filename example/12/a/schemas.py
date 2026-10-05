from pydantic import BaseModel, ConfigDict, Field


# What the client sends to /register: a plain-text password, over HTTPS.
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


# What goes back out. No password, no hash: response_model drops
# hashed_password even though the route returns the full row.
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
