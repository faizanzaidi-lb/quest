# quest_catalog_service.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# SQLite connection
def get_db():
    conn = sqlite3.connect("quest_catalog.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

# Initialize the database
def init_db():
    conn = sqlite3.connect("quest_catalog.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Quests (
            quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            reward_item TEXT NOT NULL,
            reward_qty INTEGER NOT NULL,
            auto_claim BOOLEAN NOT NULL,
            streak INTEGER NOT NULL,
            duplication INTEGER NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()

    # Insert 'sign-in-three-times' quest if it doesn't exist
    conn = sqlite3.connect("quest_catalog.db")
    cursor = conn.cursor()
    cursor.execute("SELECT quest_id FROM Quests WHERE name = 'Sign in Three Times'")
    if cursor.fetchone() is None:
        cursor.execute(
            """
            INSERT INTO Quests (name, description, reward_item, reward_qty, auto_claim, streak, duplication)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                'Sign in Three Times',
                'Log in three times to earn 10 diamonds.',
                'diamond',
                10,
                False,
                3,
                2
            )
        )
        conn.commit()
    conn.close()

init_db()

# Pydantic models
class Quest(BaseModel):
    name: str
    description: str
    reward_item: str
    reward_qty: int
    auto_claim: bool
    streak: int
    duplication: int

# Get all quests endpoint
@app.get("/quests/")
def get_quests(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Quests")
    quests = cursor.fetchall()
    return [
        {
            "quest_id": quest[0],
            "name": quest[1],
            "description": quest[2],
            "reward_item": quest[3],
            "reward_qty": quest[4],
            "auto_claim": bool(quest[5]),
            "streak": quest[6],
            "duplication": quest[7]
        }
        for quest in quests
    ]

# Get quest by ID endpoint
@app.get("/quests/{quest_id}")
def get_quest(quest_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Quests WHERE quest_id = ?", (quest_id,))
    quest = cursor.fetchone()
    if quest:
        return {
            "quest_id": quest[0],
            "name": quest[1],
            "description": quest[2],
            "reward_item": quest[3],
            "reward_qty": quest[4],
            "auto_claim": bool(quest[5]),
            "streak": quest[6],
            "duplication": quest[7]
        }
    else:
        raise HTTPException(status_code=404, detail="Quest not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
