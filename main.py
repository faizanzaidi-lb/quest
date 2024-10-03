import sqlite3
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel

# SQLite database connection
conn = sqlite3.connect("rewards_system.db", check_same_thread=False)
cursor = conn.cursor()


def get_db():
    conn = sqlite3.connect("rewards_system.db")
    try:
        yield conn
    finally:
        conn.close()


# Create Users table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    gold INTEGER DEFAULT 0,
    diamond INTEGER DEFAULT 0,
    status INTEGER NOT NULL
);
"""
)

# Create Rewards table
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

# Create Quest table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Quests (
    quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reward_id INTEGER,
    auto_claim BOOLEAN NOT NULL,
    streak INTEGER NOT NULL,
    duplication INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (reward_id) REFERENCES Rewards(reward_id)
);
"""
)

# Create User_Quest_Rewards table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS User_Quest_Rewards (
    user_id INTEGER,
    quest_id INTEGER,
    status TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (quest_id) REFERENCES Quests(quest_id),
    PRIMARY KEY (user_id, quest_id)
);
"""
)

conn.commit()

# FastAPI app
app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define Pydantic models
class User(BaseModel):
    user_id: int
    user_name: str
    gold: int
    diamond: int
    status: int


class UserCreate(BaseModel):
    user_name: str
    status: int


class Quest(BaseModel):
    quest_id: int
    reward_id: int
    auto_claim: bool
    streak: int
    duplication: int
    name: str
    description: str


class QuestCreate(BaseModel):  # New model for quest creation
    reward_id: int
    auto_claim: bool
    streak: int
    duplication: int
    name: str
    description: str


# Get Users endpoint
@app.get("/users/", response_model=List[User])
def get_users(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    return [
        {
            "user_id": user[0],
            "user_name": user[1],
            "gold": user[2],
            "diamond": user[3],
            "status": user[4],
        }
        for user in users
    ]


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


# Create User endpoint
@app.post("/users/")
def create_user(user: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Users (user_name, status) VALUES (?, ?)",
            (user.user_name, user.status),
        )
        db.commit()
        return {"message": "User created successfully"}
    except sqlite3.IntegrityError as e:
        return JSONResponse(
            status_code=400, content={"message": "Integrity error: " + str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": "Internal server error: " + str(e)}
        )


# Create Quest endpoint
@app.post("/quests/")
def create_quest(quest: QuestCreate, db: sqlite3.Connection = Depends(get_db)):
    print("Received quest data:", quest)  # Use the new model
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
        return {"message": "Quest created successfully"}
    except sqlite3.IntegrityError as e:
        return JSONResponse(
            status_code=400, content={"message": "Integrity error: " + str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": "Internal server error: " + str(e)}
        )


# Create Reward endpoint
@app.post("/rewards/")
def create_reward(
    reward_name: str,
    reward_item: str,
    reward_qty: int,
    db: sqlite3.Connection = Depends(get_db),
):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
        INSERT INTO Rewards (reward_name, reward_item, reward_qty)
        VALUES (?, ?, ?)
        """,
            (reward_name, reward_item, reward_qty),
        )
        db.commit()
        return {"message": "Reward created successfully"}
    except sqlite3.IntegrityError as e:
        return JSONResponse(
            status_code=400, content={"message": "Integrity error: " + str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": "Internal server error: " + str(e)}
        )


# Create User-Quest-Reward endpoint
@app.post("/user-quest-rewards/")
def create_user_quest_reward(
    user_id: int, quest_id: int, status: str, db: sqlite3.Connection = Depends(get_db)
):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
        INSERT INTO User_Quest_Rewards (user_id, quest_id, status)
        VALUES (?, ?, ?)
        """,
            (user_id, quest_id, status),
        )
        db.commit()
        return {"message": "User quest reward created successfully"}
    except sqlite3.IntegrityError as e:
        return JSONResponse(
            status_code=400, content={"message": "Integrity error: " + str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": "Internal server error: " + str(e)}
        )


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
