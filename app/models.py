from sqlalchemy import Column, Integer, String
from .database import Base

class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    pending = Column(Integer, default=0)
    completed = Column(Integer, default=0)
    predicted = Column(Integer, default=0)