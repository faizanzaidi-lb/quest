# auth_service.py

import sqlite3
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
import datetime

# Constants for JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()


# Database initialization
def get_db():
    conn = sqlite3.connect("auth.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect("auth.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            status INTEGER NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


init_db()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str
    status: int


class User(BaseModel):
    user_id: int
    username: str
    status: int


class Token(BaseModel):
    access_token: str
    token_type: str


# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user(db, username: str):
    cursor = db.cursor()
    cursor.execute(
        "SELECT user_id, username, hashed_password, status FROM Users WHERE username = ?",
        (username,),
    )
    row = cursor.fetchone()
    if row:
        return {
            "user_id": row[0],
            "username": row[1],
            "hashed_password": row[2],
            "status": row[3],
        }
    return None


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


# Routes
@app.post("/register/", response_model=User)
def register(user: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    hashed_password = get_password_hash(user.password)
    try:
        cursor.execute(
            "INSERT INTO Users (username, hashed_password, status) VALUES (?, ?, ?)",
            (user.username, hashed_password, user.status),
        )
        db.commit()
        user_id = cursor.lastrowid
        return {"user_id": user_id, "username": user.username, "status": user.status}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already registered")


@app.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: sqlite3.Connection = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(
    token: str = Depends(oauth2_scheme), db: sqlite3.Connection = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, username)
    if user is None:
        raise credentials_exception
    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "status": user["status"],
    }


@app.get("/users/me/", response_model=User)
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "status": current_user["status"],
    }
