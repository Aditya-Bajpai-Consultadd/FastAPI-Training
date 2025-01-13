from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    password: str
    role: str

    class Config:
        orm_mode = True


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    available: bool

    class Config:
        orm_mode = True

class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    available: int

class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    available: bool | None = None

class BorrowRequest(BaseModel):
    book_id: int

class BorrowResponse(BaseModel):
    message: str

class ReturnRequest(BaseModel):
    book_id: int

class ReturnResponse(BaseModel):
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    role: str 