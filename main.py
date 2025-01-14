from fastapi import FastAPI, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
import jwtToken
from database import engine, get_db
from schema import Base, Book, User
from models import  BookResponse, BookCreate, BookUpdate, BorrowRequest, BorrowResponse, ReturnRequest, ReturnResponse, Token, UserCreate, UserModel

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/')
def index():
    return {'data': {'name': 'Aditya'}}


@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = jwtToken.get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "user successfully created"}

@app.post("/login", response_model=Token)
def login(form_data: jwtToken.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not jwtToken.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = jwtToken.create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/admin/books", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db), user: jwtToken.TokenData = Depends(jwtToken.admin_only)):
    books = db.query(Book).all()
    if not books:
        raise HTTPException(status_code=404, detail="No books found")
    return books

@app.post("/admin/books")
def add_book(book: BookCreate, db: Session = Depends(get_db), user: jwtToken.TokenData = Depends(jwtToken.admin_only)):
    existing_book = db.query(Book).filter(Book.title == book.title, Book.author == book.author).first()
    if existing_book:
        raise HTTPException(status_code=400, detail="Book with this title and author already exists")
    new_book = Book(
        title=book.title,
        author=book.author,
        genre=book.genre,
        available=book.available
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return ({"message": "Book added successfully", "data": new_book})

@app.put("/admin/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_data: BookUpdate, db: Session = Depends(get_db),user: jwtToken.TokenData = Depends(jwtToken.admin_only)):
    # Find the book by ID
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book_data.title is not None:
        book.title = book_data.title
    if book_data.author is not None:
        book.author = book_data.author
    if book_data.genre is not None:
        book.genre = book_data.genre
    if book_data.available is not None:
        book.available = book_data.available
    db.commit()
    db.refresh(book)
    return book

@app.delete("/admin/books/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db),user: jwtToken.TokenData = Depends(jwtToken.admin_only)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return ({"message": "Book deleted successfully"})

@app.get("/books", response_model=list[BookResponse])
def search_books(
    search: str = Query(..., description="Search by title, author, or genre"),
    db: Session = Depends(get_db), user: jwtToken.TokenData = Depends(jwtToken.user_only)
):
    books = db.query(Book).filter(
        (Book.title.ilike(f"%{search}%")) |
        (Book.author.ilike(f"%{search}%")) |
        (Book.genre.ilike(f"%{search}%"))
    ).all()
    if not books:
        return []
    return books

@app.post("/borrow", response_model=BorrowResponse)
def borrow_book(borrow_data: BorrowRequest, db: Session = Depends(get_db),user: jwtToken.TokenData = Depends(jwtToken.user_only)):
    book = db.query(Book).filter(Book.id == borrow_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.available:
        raise HTTPException(status_code=400, detail="Book is not available")
    book.available = False
    db.commit()
    return {"message": f"You have successfully borrowed '{book.title}'"}

@app.post("/return", response_model=ReturnResponse)
def return_book(return_data: ReturnRequest, db: Session = Depends(get_db),user: jwtToken.TokenData = Depends(jwtToken.user_only)):
    book = db.query(Book).filter(Book.id == return_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.available:
        raise HTTPException(status_code=400, detail="Book is not borrowed")
    book.available = True
    db.commit()
    return {"message": f"You have successfully returned '{book.title}'"}
