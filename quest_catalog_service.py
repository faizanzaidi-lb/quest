# quest_catalog_service.py

import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()


# Database initialization
def get_db():
    conn = sqlite3.connect("quest_catalog.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


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


# Pydantic models
class Quest(BaseModel):
    quest_id: int
    reward_id: Optional[int]
    auto_claim: bool
    streak: int
    duplication: int
    name: str
    description: str


class QuestCreate(BaseModel):
    reward_id: Optional[int]
    auto_claim: bool
    streak: int
    duplication: int
    name: str
    description: str


class QuestUpdate(BaseModel):
    reward_id: Optional[int] = None
    auto_claim: Optional[bool] = None
    streak: Optional[int] = None
    duplication: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None


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


@app.get("/quests/{quest_id}/", response_model=Quest)
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
    raise HTTPException(status_code=404, detail="Quest not found")


@app.post("/quests/", response_model=Quest)
def create_quest(quest: QuestCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Quests (reward_id, auto_claim, streak, duplication, name, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                quest.reward_id,
                int(quest.auto_claim),
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
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))


@app.put("/quests/{quest_id}/", response_model=Quest)
def update_quest(
    quest_id: int, quest: QuestUpdate, db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Quests WHERE quest_id = ?", (quest_id,))
    existing_quest = cursor.fetchone()
    if not existing_quest:
        raise HTTPException(status_code=404, detail="Quest not found")

    update_data = quest.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "auto_claim":
            value = int(value)
        cursor.execute(
            f"UPDATE Quests SET {key} = ? WHERE quest_id = ?", (value, quest_id)
        )
    db.commit()

    cursor.execute("SELECT * FROM Quests WHERE quest_id = ?", (quest_id,))
    updated_quest = cursor.fetchone()
    return {
        "quest_id": updated_quest[0],
        "reward_id": updated_quest[1],
        "auto_claim": bool(updated_quest[2]),
        "streak": updated_quest[3],
        "duplication": updated_quest[4],
        "name": updated_quest[5],
        "description": updated_quest[6],
    }


@app.delete("/quests/{quest_id}/")
def delete_quest(quest_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Quests WHERE quest_id = ?", (quest_id,))
    quest = cursor.fetchone()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    cursor.execute("DELETE FROM Quests WHERE quest_id = ?", (quest_id,))
    db.commit()
    return {"message": "Quest deleted successfully"}
