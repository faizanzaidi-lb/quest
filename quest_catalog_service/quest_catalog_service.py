import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel

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

# SQLite database connection for the Quest Catalog Service
def get_db():
    conn = sqlite3.connect("quest_catalog.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

# Create tables if they don't exist
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
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Rewards (
            reward_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reward_name TEXT NOT NULL,
            reward_item TEXT NOT NULL,
            reward_qty INTEGER NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()

# Call to initialize the database
init_db()

# Define Pydantic models
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


class Reward(BaseModel):
    reward_id: int
    reward_name: str
    reward_item: str
    reward_qty: int


class RewardCreate(BaseModel):
    reward_name: str
    reward_item: str
    reward_qty: int


# Get Quests endpoint
@app.get("/quests/", response_model=List[Quest])
def get_quests(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Quests")
    quests = cursor.fetchall()
    return [
        {
            "quest_id": quest[0],
            "reward_id": quest[1],
            "auto_claim": quest[2],
            "streak": quest[3],
            "duplication": quest[4],
            "name": quest[5],
            "description": quest[6],
        }
        for quest in quests
    ]


# Create Quest endpoint
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
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Integrity error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))


# Get Rewards endpoint
@app.get("/rewards/")
def get_rewards(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM Rewards")
        rewards = cursor.fetchall()
        return [
            {
                "reward_id": reward[0],
                "reward_name": reward[1],
                "reward_item": reward[2],
                "reward_qty": reward[3],
            }
            for reward in rewards
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))


# Create Reward endpoint
@app.post("/rewards/", response_model=Reward)
def create_reward(reward: RewardCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO Rewards (reward_name, reward_item, reward_qty)
            VALUES (?, ?, ?)
            """,
            (reward.reward_name, reward.reward_item, reward.reward_qty),
        )
        db.commit()
        reward_id = cursor.lastrowid
        return {**reward.dict(), "reward_id": reward_id}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Integrity error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))


# Get Quests with Rewards endpoint
@app.get("/quests-with-rewards/")
def get_quests_with_rewards(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT q.quest_id, q.reward_id, q.auto_claim, q.streak, q.duplication, q.name, q.description, 
               r.reward_name, r.reward_item, r.reward_qty 
        FROM Quests q
        LEFT JOIN Rewards r ON q.reward_id = r.reward_id
        """
    )
    quests_with_rewards = cursor.fetchall()

    quests = []
    for quest in quests_with_rewards:
        quests.append(
            {
                "quest_id": quest[0],
                "reward_id": quest[1],
                "auto_claim": quest[2],
                "streak": quest[3],
                "duplication": quest[4],
                "name": quest[5],
                "description": quest[6],
                "reward_name": quest[7],
                "reward_item": quest[8],
                "reward_qty": quest[9],
            }
        )
    return quests


# Run the app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
