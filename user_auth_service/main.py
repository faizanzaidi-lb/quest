from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel
import sqlite3
import requests

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SQLite connection
def get_db():
    conn = sqlite3.connect("user_auth.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

# Initialize the database
def init_db():
    conn = sqlite3.connect("user_auth.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class User(BaseModel):
    username: str
    password: str

class UserListResponse(BaseModel):
    user_id: int
    username: str

# Model for logout request
class LogoutRequest(BaseModel):
    user_id: int

# Hash password utility
def hash_password(password: str):
    return pwd_context.hash(password)

# Verify password utility
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Register endpoint
@app.post("/register")
def register(user: User, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    try:
        hashed_password = hash_password(user.password)
        cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (user.username, hashed_password))
        db.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")

# Login endpoint
@app.post("/login")
def login(user: User, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT user_id, password FROM Users WHERE username = ?", (user.username,))
    result = cursor.fetchone()
    if not result or not verify_password(user.password, result[1]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    user_id = result[0]
    
    # Notify Quest Processing Service about the login event
    try:
        response = requests.post(
            "http://localhost:8003/track-login/",
            json={"user_id": user_id}
        )
        if response.status_code != 200:
            print("Failed to notify Quest Processing Service")
    except Exception as e:
        print(f"Error communicating with Quest Processing Service: {e}")
    
    return {"message": "Login successful", "user_id": user_id}

@app.post("/logout")
def logout(logout_request: LogoutRequest, db: sqlite3.Connection = Depends(get_db)):
    # You can add any logout logic here if needed
    return {"message": "Logout successful"}

# Endpoint to get all users
@app.get("/users", response_model=list[UserListResponse])
def get_users(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT user_id, username FROM Users")
    users = cursor.fetchall()
    
    return [{"user_id": user[0], "username": user[1]} for user in users]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
