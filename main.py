from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import sqlite3

app = FastAPI()

DATABASE = "quest.db"


# Quest and UserQuest schemas
class Quest(BaseModel):
    name: str
    description: str


class UserQuest(BaseModel):
    user_id: int
    quest_id: int


# Connect to the SQLite database
def get_db():
    conn = sqlite3.connect(DATABASE)
    yield conn
    conn.close()


# Create quests and user_quests tables
with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quest_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'not_claimed'
        )
    """
    )


@app.post("/create-quest")
async def create_quest(quest: Quest, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO quests (name, description) VALUES (?, ?)",
        (quest.name, quest.description),
    )
    db.commit()
    return {"message": "Quest created successfully"}


@app.post("/assign-quest")
async def assign_quest(user_quest: UserQuest, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM quests WHERE id = ?", (user_quest.quest_id,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Quest not found")

    cursor.execute(
        "INSERT INTO user_quests (user_id, quest_id) VALUES (?, ?)",
        (user_quest.user_id, user_quest.quest_id),
    )
    db.commit()
    return {"message": "Quest assigned to user"}


@app.get("/user-quests/{user_id}")
async def get_user_quests(user_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT quest_id, status FROM user_quests WHERE user_id = ?", (user_id,)
    )
    quests = cursor.fetchall()

    if not quests:
        raise HTTPException(status_code=404, detail="No quests found for user")

    return {
        "user_quests": [{"quest_id": quest[0], "status": quest[1]} for quest in quests]
    }
