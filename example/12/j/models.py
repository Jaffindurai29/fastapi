from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from database import Base


class UserModel(Base):
    __tablename__ = "secure_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    # Only ever the argon2 hash, never the password itself.
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)


class NoteModel(Base):
    __tablename__ = "secure_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    body = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("secure_users.id"), nullable=False)


class RefreshTokenModel(Base):
    # One row per refresh token ever issued, keyed by its "jti" (a random
    # id inside the token). This is what makes rotation real: a used or
    # revoked refresh token is rejected even though its signature and
    # expiry are still fine.
    __tablename__ = "secure_refresh_tokens"

    jti = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("secure_users.id"), nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
