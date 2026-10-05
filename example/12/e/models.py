from sqlalchemy import Column, Integer, String

from database import Base


# 12/f uses this exact same table, so keep the two models identical.
class UserModel(Base):
    __tablename__ = "sec_rbac_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    # "user" or "admin". A plain string column is enough for two roles.
    role = Column(String(20), nullable=False, default="user")
