from datetime import datetime
import logging
from enum import Enum

from pydantic import BaseModel, Field, field_validator
from typing import Optional

from constants.roles import Roles


logger = logging.getLogger(__name__)
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

class TestUser(BaseModel):
    email: str = Field(... , pattern=EMAIL_PATTERN)
    fullName: str = Field(... , min_length=1, max_length=100)
    password: str = Field(... , min_length=8, max_length=20)
    passwordRepeat: str = Field(... , min_length=8, max_length=20)
    roles: list[Roles] = [Roles.USER]
    verified: Optional[bool] = None
    banned: Optional[bool] = None
    id: Optional[str] = None


    @field_validator("passwordRepeat")
    @classmethod
    def check_password_repeat(cls, value, info):
        print("Валидатор запущен!")
        print("value:", value)
        print("info.data:", info.data)
        if 'password' in info.data and info.data['password'] != value:
            raise ValueError("Пароли не совпадают")

        return value

class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(..., pattern=EMAIL_PATTERN)
    fullName: str = Field(..., min_length=1, max_length=100)
    verified: bool
    roles: list[Roles]
    createdAt: datetime
    banned: bool

class Genre(BaseModel):
    name: str

class GenreResponse(BaseModel):
    id: int
    name: str

class Location(str, Enum):
    MSK = 'MSK'
    SPB = 'SPB'

class Movie(BaseModel):
    id: int
    name: str
    description: str
    genreId: int
    imageUrl: str | None
    price: int
    rating: float = Field(..., ge=0, le=5)
    location: Location
    published: bool
    createdAt: datetime
    genre: Genre

class MoviesPage(BaseModel):
    movies: list[Movie]
    count: int
    page: int
    pageSize: int
    pageCount: int