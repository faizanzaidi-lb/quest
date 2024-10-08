# auth_service.py

import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import hashlib
import jwt
import datetime
import requests

SECRET_KEY = "your_secret_key"  # Replace with a secure secret key in production
QUEST_PROCESSING_SERVICE_URL = "http://localhost:8003/track-sign-in/"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    conn = sqlite3.connect("auth.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
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
            user_name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            gold INTEGER DEFAULT 0,
            diamond INTEGER DEFAULT 0,
            status INTEGER NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


# Pydantic Models
class UserCreate(BaseModel):
    user_name: str
    password: str
    status: str


class UserLogin(BaseModel):
    user_name: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    user_id: int
    user_name: str
    gold: int
    diamond: int
    status: str


class AddDiamonds(BaseModel):
    diamonds: Optional[int] = None
    gold: Optional[int] = None


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        hashed_password = hash_password(user.password)
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Users (user_name, password, status) VALUES (?, ?, ?)",
            (user.user_name, hashed_password, user.status),
        )
        db.commit()
        user_id = cursor.lastrowid

        cursor.execute(
            "UPDATE Users SET gold = gold + 20 WHERE user_id = ?", (user_id,)
        )
        db.commit()

        token = create_token(user_id)
        return {"access_token": token, "token_type": "bearer"}

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login", response_model=Token)
def login(user: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    try:
        hashed_password = hash_password(user.password)
        cursor = db.cursor()
        cursor.execute(
            "SELECT user_id FROM Users WHERE user_name = ? AND password = ?",
            (user.user_name, hashed_password),
        )
        result = cursor.fetchone()
        if result:
            user_id = result["user_id"]

            try:
                response = requests.post(
                    QUEST_PROCESSING_SERVICE_URL, json={"user_id": user_id}
                )
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=500, detail="Failed to track quest progress"
                    )
            except requests.exceptions.RequestException:
                raise HTTPException(
                    status_code=500, detail="Quest Processing service unavailable"
                )

            token = create_token(user_id)
            return {"access_token": token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT user_id, user_name, gold, diamond, status FROM Users WHERE user_id = ?",
        (user_id,),
    )
    user = cursor.fetchone()
    if user:
        status_map = {0: "new", 1: "not_new", 2: "banned"}
        return UserResponse(
            user_id=user["user_id"],
            user_name=user["user_name"],
            gold=user["gold"],
            diamond=user["diamond"],
            status=status_map.get(user["status"], "unknown"),
        )
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/add-diamonds/{user_id}/")
def add_diamonds(
    user_id: int, data: AddDiamonds, db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    if data.diamonds is not None:
        cursor.execute(
            "UPDATE Users SET diamond = diamond + ? WHERE user_id = ?",
            (data.diamonds, user_id),
        )
    if data.gold is not None:
        cursor.execute(
            "UPDATE Users SET gold = gold + ? WHERE user_id = ?", (data.gold, user_id)
        )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    db.commit()
    return {"message": "Rewards added successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
