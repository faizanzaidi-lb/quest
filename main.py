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


# SQLite database connection
def get_db():
    conn = sqlite3.connect(
        "rewards_system.db", check_same_thread=False
    ) 
    try:
        yield conn
    finally:
        conn.close()


# Create tables if they don't exist
def init_db():
    conn = sqlite3.connect("rewards_system.db")
    cursor = conn.cursor()
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
    conn.close()


# Call to initialize the database
init_db()


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


class UserQuestReward(BaseModel):
    user_id: int
    quest_id: int
    status: str


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


# Create User endpoint
@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Users (user_name, status) VALUES (?, ?)",
            (user.user_name, user.status),
        )
        db.commit()
        user_id = cursor.lastrowid
        return {
            "user_id": user_id,
            "user_name": user.user_name,
            "gold": 0,  # Default value for gold
            "diamond": 0,  # Default value for diamond
            "status": user.status,
        }
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Integrity error: " + str(e))
    except Exception as e:
        print(f"Error occurred while creating user: {e}")  # Log the error
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))


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
        print(f"Error occurred while fetching quests: {e}")  # Log the error
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
        print(f"Error occurred while fetching rewards: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


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


# Assign Quest to User endpoint
@app.post("/user-quest-rewards/")
def create_user_quest_reward(
    user_quest_reward: UserQuestReward, db: sqlite3.Connection = Depends(get_db)
):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO User_Quest_Rewards (user_id, quest_id, status)
            VALUES (?, ?, ?)
            """,
            (
                user_quest_reward.user_id,
                user_quest_reward.quest_id,
                user_quest_reward.status,
            ),
        )
        db.commit()
        return {"message": "User quest reward created successfully"}
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


class AssignQuest(BaseModel):
    user_id: int
    quest_id: int


# Assign Quest endpoint
@app.post("/assign-quest/")
def assign_quest(assign_quest: AssignQuest, db: sqlite3.Connection = Depends(get_db)):
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
    except sqlite3.IntegrityError as e:
        return JSONResponse(
            status_code=400, content={"message": "Integrity error: " + str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": "Internal server error: " + str(e)}
        )
        
        
# Get User Quests endpoint
@app.get("/user-quests/{user_id}")
def get_user_quests(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT uq.user_id, uq.quest_id, uq.status, q.name, q.description
        FROM User_Quest_Rewards uq
        JOIN Quests q ON uq.quest_id = q.quest_id
        WHERE uq.user_id = ?
        """,
        (user_id,),
    )
    user_quests = cursor.fetchall()

    return [
        {
            "user_id": user_quest[0],
            "quest_id": user_quest[1],
            "status": user_quest[2],
            "quest_name": user_quest[3],
            "quest_description": user_quest[4],
        }
        for user_quest in user_quests
    ]


# Run the app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
