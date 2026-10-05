from sqlalchemy import Column, Integer, String

from database import Base


class UserModel(Base):
    __tablename__ = "sec_a_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), nullable=False, unique=True)
    # Only the HASH is stored. There is no "password" column at all.
    # 255 leaves room: an Argon2 hash is ~97 characters.
    hashed_password = Column(String(255), nullable=False)
