from sqlalchemy import Column, ForeignKey, Integer, String, Text

from database import Base


# Identical to 12/e's model, so both lessons share the same table.
class UserModel(Base):
    __tablename__ = "sec_rbac_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    # "user" or "admin". A plain string column is enough for two roles.
    role = Column(String(20), nullable=False, default="user")


class NoteModel(Base):
    __tablename__ = "sec_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    body = Column(Text, nullable=False, default="")
    # Who owns this row. Every permission check compares against it.
    # ondelete="CASCADE": when 12/e's admin deletes a user, MySQL deletes
    # their notes too instead of refusing the delete.
    owner_id = Column(
        Integer, ForeignKey("sec_rbac_users.id", ondelete="CASCADE"), nullable=False, index=True
    )
