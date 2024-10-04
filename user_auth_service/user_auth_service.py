import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional

# Create FastAPI app
app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SQLite database connection
def get_db():
    conn = sqlite3.connect("auth_service.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


# Create tables for the User Authentication Service
def init_db():
    conn = sqlite3.connect("auth_service.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            status INTEGER NOT NULL DEFAULT 1
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        );
        """
    )
    conn.commit()
    conn.close()

# Call to initialize the database
init_db()

# Define Pydantic models
class UserRegister(BaseModel):
    user_name: str
    password: str
    email: str


class UserLogin(BaseModel):
    user_name: str
    password: str


class UserSession(BaseModel):
    session_token: str


# Helper functions for hashing and verifying passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Register new user endpoint
@app.post("/register/")
def register_user(user: UserRegister, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    hashed_password = hash_password(user.password)

    try:
        cursor.execute(
            """
            INSERT INTO Users (user_name, hashed_password, email)
            VALUES (?, ?, ?)
            """,
            (user.user_name, hashed_password, user.email),
        )
        db.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# Login endpoint
@app.post("/login/")
def login_user(user: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT user_id, hashed_password FROM Users WHERE user_name = ?
        """,
        (user.user_name,),
    )
    user_record = cursor.fetchone()

    if not user_record or not verify_password(user.password, user_record[1]):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Generate a dummy session token (in a real-world scenario, you'd use JWT or another method)
    session_token = f"session_token_{user_record[0]}"

    cursor.execute(
        """
        INSERT INTO Sessions (user_id, session_token) VALUES (?, ?)
        """,
        (user_record[0], session_token),
    )
    db.commit()
    
    return {"session_token": session_token}


# Validate session endpoint
@app.post("/validate-session/")
def validate_session(session: UserSession, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT session_id FROM Sessions WHERE session_token = ?
        """,
        (session.session_token,),
    )
    session_record = cursor.fetchone()

    if not session_record:
        raise HTTPException(status_code=400, detail="Invalid session token")

    return {"message": "Session valid"}


# Logout endpoint
@app.post("/logout/")
def logout_user(session: UserSession, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        DELETE FROM Sessions WHERE session_token = ?
        """,
        (session.session_token,),
    )
    db.commit()

    return {"message": "Logged out successfully"}


# Run the app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
