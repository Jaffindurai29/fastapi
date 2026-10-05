from typing import Literal

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str


# Never includes hashed_password.
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str


# Literal: anything other than "user" or "admin" is a 422 before the
# route runs.
class RoleUpdate(BaseModel):
    role: Literal["user", "admin"]
