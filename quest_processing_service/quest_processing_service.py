from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3


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


# SQLite database connection specific to this microservice
def get_db():
    conn = sqlite3.connect("quest_processing.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


# Initialize the quest processing database and create necessary tables
def init_db():
    conn = sqlite3.connect("quest_processing.db")
    cursor = conn.cursor()

    # Create table for User Quest Rewards if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS User_Quest_Rewards (
            user_id INTEGER,
            quest_id INTEGER,
            status TEXT NOT NULL,
            diamonds INTEGER DEFAULT 0,
            gold INTEGER DEFAULT 0,  -- Added column for gold
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, quest_id)
        );
        """
    )

    # Create table for tracking sign-in attempts
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS SignInAttempts (
            user_id INTEGER PRIMARY KEY,
            sign_in_count INTEGER DEFAULT 0
        );
        """
    )

    conn.commit()
    conn.close()


# Call to initialize the database
init_db()


# Pydantic Models
class UserQuestReward(BaseModel):
    user_id: int
    quest_id: int
    status: str
    diamonds: int = 0
    gold: int = 0  # Added gold to model


# Track Sign-In Quest Progress and First Signup Reward
@app.post("/sign-in/", response_model=UserQuestReward)
def sign_in(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()

        # Check if user has received the first sign-up reward (assume quest_id = 0 for first signup)
        cursor.execute(
            """
            SELECT gold FROM User_Quest_Rewards WHERE user_id = ? AND quest_id = 0
            """, (user_id,)
        )
        first_signup_reward = cursor.fetchone()

        # If no record of the first signup reward, reward the user with 20 gold units
        if first_signup_reward is None:
            cursor.execute(
                """
                INSERT INTO User_Quest_Rewards (user_id, quest_id, status, gold)
                VALUES (?, 0, 'completed', 20)
                """, (user_id,)
            )
            db.commit()
            return {"user_id": user_id, "quest_id": 0, "status": "completed", "diamonds": 0, "gold": 20}

        # If user already received the first sign-up reward, proceed with sign-in quest
        cursor.execute(
            """
            SELECT sign_in_count FROM SignInAttempts WHERE user_id = ?
            """, (user_id,)
        )
        result = cursor.fetchone()

        # If no record, create a new entry for the user with sign-in count 1
        if result is None:
            cursor.execute(
                """
                INSERT INTO SignInAttempts (user_id, sign_in_count)
                VALUES (?, 1)
                """, (user_id,)
            )
            sign_in_count = 1
        else:
            # Update the login count
            sign_in_count = result[0] + 1
            cursor.execute(
                """
                UPDATE SignInAttempts
                SET sign_in_count = ?
                WHERE user_id = ?
                """, (sign_in_count, user_id)
            )

        # Check if the user has logged in 3 times
        if sign_in_count >= 3:
            # Reward user with 10 diamonds if quest is completed
            cursor.execute(
                """
                INSERT OR REPLACE INTO User_Quest_Rewards (user_id, quest_id, status, diamonds)
                VALUES (?, ?, 'completed', 10)
                """, (user_id, 1)  # Assume quest_id = 1 for 'sign-in-three-times'
            )
            # Reset sign_in_count to prevent further rewards for the same quest
            cursor.execute(
                """
                UPDATE SignInAttempts
                SET sign_in_count = 0
                WHERE user_id = ?
                """, (user_id,)
            )
            reward = {"user_id": user_id, "quest_id": 1, "status": "completed", "diamonds": 10, "gold": 0}
        else:
            reward = {"user_id": user_id, "quest_id": 1, "status": f"progress: {sign_in_count}/3", "diamonds": 0, "gold": 0}

        db.commit()
        return reward
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))


# Get all User Quests
@app.get("/user-quests/{user_id}/", response_model=List[UserQuestReward])
def get_user_quests(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT user_id, quest_id, status, diamonds, gold
        FROM User_Quest_Rewards
        WHERE user_id = ?
        """,
        (user_id,),
    )
    user_quests = cursor.fetchall()
    return [
        {"user_id": quest[0], "quest_id": quest[1], "status": quest[2], "diamonds": quest[3], "gold": quest[4]}
        for quest in user_quests
    ]


# Update Quest Status
@app.put("/update-quest-status/", response_model=UserQuestReward)
def update_quest_status(user_quest_reward: UserQuestReward, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE User_Quest_Rewards
            SET status = ?, diamonds = ?, gold = ?
            WHERE user_id = ? AND quest_id = ?
            """,
            (user_quest_reward.status, user_quest_reward.diamonds, user_quest_reward.gold, user_quest_reward.user_id, user_quest_reward.quest_id),
        )
        db.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Quest or User not found")

        return user_quest_reward
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Integrity error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))


# Get all Quests assigned to Users
@app.get("/all-user-quests/", response_model=List[UserQuestReward])
def get_all_user_quests(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT user_id, quest_id, status, diamonds, gold
        FROM User_Quest_Rewards
        """
    )
    user_quests = cursor.fetchall()
    return [
        {"user_id": quest[0], "quest_id": quest[1], "status": quest[2], "diamonds": quest[3], "gold": quest[4]}
        for quest in user_quests
    ]


# Run the app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
