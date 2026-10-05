from sqlalchemy import Column, Float, Integer, String, Text

from database import Base


# This class describes what the table SHOULD look like. It no longer
# creates anything: the migrations in migrations/versions/ do that.
class ItemModel(Base):
    __tablename__ = "migrated_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    # Added later by migration 0002_add_description.
    description = Column(Text, nullable=True)
