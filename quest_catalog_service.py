# quest_catalog_service.py

import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Configure CORS as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database Dependency
def get_db():
    conn = sqlite3.connect("quest_catalog.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


# Initialize Database
def init_db():
    conn = sqlite3.connect("quest_catalog.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Quests (
            quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reward_id INTEGER,
            auto_claim BOOLEAN NOT NULL,
            streak INTEGER NOT NULL,
            duplication INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


# Pydantic Models
class Quest(BaseModel):
    quest_id: int
    reward_id: int
    auto_claim: bool
    streak: int
    duplication: int
    name: str
    description: str


class QuestCreate(BaseModel):
    reward_id: int
    auto_claim: bool
    streak: int
    duplication: int
    name: str
    description: str


# Routes
@app.get("/quests/", response_model=List[Quest])
def get_quests(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Quests")
    quests = cursor.fetchall()
    return [
        {
            "quest_id": quest[0],
            "reward_id": quest[1],
            "auto_claim": bool(quest[2]),
            "streak": quest[3],
            "duplication": quest[4],
            "name": quest[5],
            "description": quest[6],
        }
        for quest in quests
    ]


@app.post("/quests/", response_model=Quest)
def create_quest(quest: QuestCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO Quests (reward_id, auto_claim, streak, duplication, name, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                quest.reward_id,
                quest.auto_claim,
                quest.streak,
                quest.duplication,
                quest.name,
                quest.description,
            ),
        )
        db.commit()
        quest_id = cursor.lastrowid
        return {**quest.dict(), "quest_id": quest_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/quests/{quest_id}", response_model=Quest)
def get_quest(quest_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Quests WHERE quest_id = ?", (quest_id,))
    quest = cursor.fetchone()
    if quest:
        return {
            "quest_id": quest[0],
            "reward_id": quest[1],
            "auto_claim": bool(quest[2]),
            "streak": quest[3],
            "duplication": quest[4],
            "name": quest[5],
            "description": quest[6],
        }
    else:
        raise HTTPException(status_code=404, detail="Quest not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
