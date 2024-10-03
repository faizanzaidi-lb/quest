from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI()

DATABASE = "quest.db"


# Quest and UserQuest schemas
class Quest(BaseModel):
    name: str
    description: str
    category: str  # New category field


class UserQuest(BaseModel):
    user_id: int
    quest_id: int


# Connect to the SQLite database
def get_db():
    conn = sqlite3.connect(DATABASE)
    yield conn
    conn.close()


# Modify the database schema to add category and history
with sqlite3.connect(DATABASE) as conn:
    # Add 'category' column to the 'quests' table if it doesn't exist
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL
        )
    """
    )

    # Add 'completed_at' column to 'user_quests' to track quest history
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quest_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'not_claimed',
            completed_at TIMESTAMP DEFAULT NULL
        )
    """
    )


# API Endpoints

# Create a new quest with category
@app.post("/create-quest")
async def create_quest(quest: Quest, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO quests (name, description, category) VALUES (?, ?, ?)",
        (quest.name, quest.description, quest.category),
    )
    db.commit()
    return {"message": "Quest created successfully", "category": quest.category}


# Assign quest to a user
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


# Mark a quest as completed and store completion time
@app.post("/complete-quest/{user_id}/{quest_id}")
async def complete_quest(user_id: int, quest_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE user_quests SET status = 'completed', completed_at = ? WHERE user_id = ? AND quest_id = ?",
        (datetime.now(), user_id, quest_id),
    )
    db.commit()
    return {"message": "Quest marked as completed"}


# Get all quests for a user with their status
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


# Get completed quests (quest history) for a user
@app.get("/completed-quests/{user_id}")
async def get_completed_quests(user_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT quest_id, completed_at FROM user_quests WHERE user_id = ? AND status = 'completed'",
        (user_id,),
    )
    quests = cursor.fetchall()

    if not quests:
        raise HTTPException(status_code=404, detail="No completed quests found")

    return {
        "completed_quests": [
            {"quest_id": quest[0], "completed_at": quest[1]} for quest in quests
        ]
    }


# Get quests by category
@app.get("/quests-by-category/{category}")
async def get_quests_by_category(category: str, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, name, description FROM quests WHERE category = ?", (category,)
    )
    quests = cursor.fetchall()

    if not quests:
        raise HTTPException(status_code=404, detail="No quests found in this category")

    return {
        "quests": [{"id": quest[0], "name": quest[1], "description": quest[2]} for quest in quests]
    }
