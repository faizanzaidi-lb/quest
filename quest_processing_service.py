# quest_processing_service.py

import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests

app = FastAPI()

# Configure CORS as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs (Ensure these match where your services are running)
AUTH_SERVICE_URL = "http://localhost:8001"
QUEST_CATALOG_URL = "http://localhost:8002"


# Database Dependency
def get_db():
    conn = sqlite3.connect("quest_processing.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


# Initialize Database
def init_db():
    conn = sqlite3.connect("quest_processing.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS User_Quest_Rewards (
            user_id INTEGER,
            quest_id INTEGER,
            status TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, quest_id)
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


# Pydantic Models
class AssignQuest(BaseModel):
    user_id: int
    quest_id: int


class UserQuestReward(BaseModel):
    user_id: int
    quest_id: int
    status: str


# Routes
@app.post("/assign-quest/")
def assign_quest(assign_quest: AssignQuest, db: sqlite3.Connection = Depends(get_db)):
    # Verify user exists using Auth Service
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/users/{assign_quest.user_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Auth service unavailable")

    # Verify quest exists using Quest Catalog Service
    try:
        response = requests.get(f"{QUEST_CATALOG_URL}/quests/{assign_quest.quest_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Quest not found")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Quest Catalog service unavailable")

    try:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO User_Quest_Rewards (user_id, quest_id, status)
            VALUES (?, ?, ?)
            """,
            (assign_quest.user_id, assign_quest.quest_id, "not_claimed"),
        )
        db.commit()
        return {"message": "Quest assigned successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Quest already assigned to user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user-quests/{user_id}/", response_model=List[UserQuestReward])
def get_user_quests(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT quest_id, status FROM User_Quest_Rewards WHERE user_id = ?
        """,
        (user_id,),
    )
    user_quests = cursor.fetchall()
    return [
        {
            "user_id": user_id,
            "quest_id": quest[0],
            "status": quest[1],
        }
        for quest in user_quests
    ]


@app.post("/complete-quest/")
def complete_quest(assign_quest: AssignQuest, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE User_Quest_Rewards
            SET status = ?
            WHERE user_id = ? AND quest_id = ?
            """,
            ("claimed", assign_quest.user_id, assign_quest.quest_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Quest assignment not found")
        db.commit()
        return {"message": "Quest completed and reward claimed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
