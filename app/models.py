from sqlalchemy import Column, Integer, String, Index
from .database import Base


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)

    # Dish name should be unique (important)
    name = Column(String, unique=True, nullable=False, index=True)

    # Orders not yet completed
    pending = Column(Integer, default=0, nullable=False)

    # Created-till-now (as per assignment)
    completed = Column(Integer, default=0, nullable=False)

    # Predicted value
    predicted = Column(Integer, default=0, nullable=False)


# Optional composite index (for faster lookups if scaling)
Index("idx_dish_name", Dish.name)