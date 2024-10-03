from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import uuid
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory quest tracking database

# In-memory database for users
users_db: Dict[str, Dict] = {}


class User(BaseModel):
    username: str
    password: str


@app.post("/signup")
def signup(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    user_id = str(uuid.uuid4())  # Auto-generate user ID
    users_db[user.username] = {"id": user_id, "password": user.password}
    return {"message": "User created", "user_id": user_id}


@app.post("/login")
def login(user: User):
    stored_user = users_db.get(user.username)
    if not stored_user or stored_user["password"] != user.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"message": "Login successful", "user_id": stored_user["id"]}
