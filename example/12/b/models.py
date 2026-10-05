from sqlalchemy import Boolean, Column, Integer, String

from database import Base


# Shared by 12/b, 12/c, 12/d and 12/i. Keep it identical in all four:
# create_all never alters an existing table.
class UserModel(Base):
    __tablename__ = "sec_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
