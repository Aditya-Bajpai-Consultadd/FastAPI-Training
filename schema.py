from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"
    username = Column(String, unique=True,nullable=False,primary_key=True)
    password = Column(String,nullable=False)
    role = Column(String,nullable=False)


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    available = Column(Integer, default=True)