from sqlalchemy import Column, Integer, String, Text

from database import Base


class CustomerModel(Base):
    __tablename__ = "sec_customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Stored as plain text: we need to search and sort by these.
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    # Stored encrypted. Text, because ciphertext is much longer than the
    # original (a 13-character phone becomes ~100 characters).
    phone_encrypted = Column(Text, nullable=False)
    notes_encrypted = Column(Text, nullable=True)
