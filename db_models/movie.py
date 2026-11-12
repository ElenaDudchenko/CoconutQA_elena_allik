from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Boolean, Float
from sqlalchemy import DateTime
from sqlalchemy.orm import declarative_base

from constants.location import Location

Base = declarative_base()

class MovieDBModel(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    image_url= Column(String)
    location = Column(
        SQLEnum(Location, name="Location", schema="public"),
        nullable=False
    )
    published = Column(Boolean, nullable=False)
    rating = Column(Float, nullable=False)
    genre_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)