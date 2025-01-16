from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine,StaticPool
from main import app
from unittest.mock import MagicMock
from models import TokenData
from jwtToken import admin_only, get_password_hash
from database import Base,get_db
from schema import User
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)


session = TestingSessionLocal()
db_item =User(username="testadmin@gmail.com", password=get_password_hash("adminpass"), role="Admin")
session.add(db_item)
db_item1 = User(username="testuser@gmail.com", password=get_password_hash("userpass"), role="User")
session.add(db_item1)
session.commit()
session.close()


def test_read_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'data': {'name': 'Aditya'}}

#def test_registerSuccess():
 #   response = client.post("/register", json={"username": "new@gmail.com", "password": "adminpass", "role": "Admin"})
 #   assert response.status_code == 200
 #   assert "data" in response.json()
#  assert response.json()["message"] == "User registered successfully"

def test_registerFailureRole():
    response = client.post("/register", json={"username": "testadmin@gmail.com", "password":"adminpass" "adminpass", "role": "Admin"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_registerFailureUsername():
    response = client.post("/register", json={"username": "", "password": "adminpass", "role": "Admin"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid username"

def test_registerFailurePassword():
    response = client.post("/register", json={"username": "newgmail.com", "password": "", "role": "Admin"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid password"

def test_loginSuccessAdmin():
    response = client.post("/login", data={"username": "testadmin@gmail.com", "password": "adminpass", "role": "Admin"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
def test_loginSuccessUser():
    response = client.post("/login", data={"username": "testuser@gmail.com", "password": "userpass", "role": "User"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_loginFailure():
    response = client.post("/login", data={"username": "testuser", "password": "testpass", "role": "User"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"




def test_addBookSuccess():
    mock_admin_only = MagicMock(return_value=TokenData(username="admin@gmail.com", role="Admin"))
    app.dependency_overrides = {"jwtToken.admin_only": mock_admin_only}
    response = client.post("/admin/books",json={"title": "Test Book","author": "Test Author","genre": "Fiction","available": True})
    assert response.status_code == 200
    assert "data" in response.json()
    assert response.json()["message"] == "Book added successfully"
    app.dependency_overrides = {}

def test_viewBooksSuccess():
    mock_admin_only = MagicMock(return_value=TokenData(username="admin@gmail.com", role="Admin"))
    app.dependency_overrides[admin_only] = mock_admin_only
    
    response = client.get("/admin/books")
    assert response.status_code == 200

    assert response.json() == []
    app.dependency_overrides = {}

def test_viewBooksFailure():
    mock_admin_only = MagicMock(return_value=TokenData(username="testadmin@gmail.com", role="Admin"))
    app.dependency_overrides[admin_only] = mock_admin_only

    response = client.get("/admin/books")
    assert response.status_code == 404
    assert response.json()["detail"] == "No books found"
    app.dependency_overrides = {}
