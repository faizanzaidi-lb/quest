# quest_processing_service.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import sqlite3
import requests
app = FastAPI()
# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# SQLite connection
def get_db():
    conn = sqlite3.connect("quest_processing.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

# Initialize the database
def init_db():
    conn = sqlite3.connect("quest_processing.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS UserQuestProgress (
            user_id INTEGER,
            quest_id INTEGER,
            progress INTEGER DEFAULT 0,
            times_completed INTEGER DEFAULT 0,
            status TEXT DEFAULT 'not_claimed',
            PRIMARY KEY (user_id, quest_id)
        );
        """
    )
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class LoginEvent(BaseModel):
    user_id: int

# Handle login event
@app.post("/track-login/")
def track_login(event: LoginEvent, db: sqlite3.Connection = Depends(get_db)):
    user_id = event.user_id

    # Get the 'sign-in-three-times' quest details from Quest Catalog Service
    try:
        response = requests.get("http://localhost:8002/quests/")
        quests = response.json()
        sign_in_quest = None
        for quest in quests:
            if quest['name'] == 'Sign in Three Times':
                sign_in_quest = quest
                break
        if not sign_in_quest:
            raise Exception("Quest not found in Quest Catalog Service")
    except Exception as e:
        print(f"Error fetching quest details: {e}")
        raise HTTPException(status_code=500, detail="Error fetching quest details")

    quest_id = sign_in_quest['quest_id']
    streak = sign_in_quest['streak']
    duplication = sign_in_quest['duplication']

    cursor = db.cursor()

    # Check if the user has an entry for this quest
    cursor.execute(
        """
        SELECT progress, times_completed, status FROM UserQuestProgress
        WHERE user_id = ? AND quest_id = ?
        """,
        (user_id, quest_id)
    )
    result = cursor.fetchone()

    if result:
        progress, times_completed, status = result
        # Check if the user has completed the quest the maximum number of times
        if times_completed >= duplication:
            return {"message": "Quest already completed maximum number of times"}

        # Increment progress
        progress += 1

        # Check if the quest is completed
        if progress >= streak:
            times_completed += 1
            progress = 0  # Reset progress
            status = 'not_claimed'  # Ready to be claimed

            # Update the user's progress
            cursor.execute(
                """
                UPDATE UserQuestProgress
                SET progress = ?, times_completed = ?, status = ?
                WHERE user_id = ? AND quest_id = ?
                """,
                (progress, times_completed, status, user_id, quest_id)
            )
            db.commit()
            return {"message": "Quest completed! Reward is ready to be claimed."}
        else:
            # Update progress
            cursor.execute(
                """
                UPDATE UserQuestProgress
                SET progress = ?
                WHERE user_id = ? AND quest_id = ?
                """,
                (progress, user_id, quest_id)
            )
            db.commit()
            return {"message": f"Progress updated: {progress}/{streak}"}
    else:
        # First time tracking progress for this user and quest
        progress = 1
        times_completed = 0
        status = 'in_progress'
        cursor.execute(
            """
            INSERT INTO UserQuestProgress (user_id, quest_id, progress, times_completed, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, quest_id, progress, times_completed, status)
        )
        db.commit()
        return {"message": f"Progress started: {progress}/{streak}"}

# Endpoint to get user's quest progress
@app.get("/user-quests/{user_id}")
def get_user_quests(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT quest_id, progress, times_completed, status FROM UserQuestProgress
        WHERE user_id = ?
        """,
        (user_id,)
    )
    user_quests = cursor.fetchall()
    quests = []
    for uq in user_quests:
        quest_id, progress, times_completed, status = uq
        # Get quest details from Quest Catalog Service
        try:
            response = requests.get(f"http://localhost:8002/quests/{quest_id}")
            if response.status_code == 200:
                quest = response.json()
                quests.append({
                    "quest_id": quest_id,
                    "name": quest['name'],
                    "description": quest['description'],
                    "progress": progress,
                    "streak": quest['streak'],
                    "times_completed": times_completed,
                    "duplication": quest['duplication'],
                    "status": status
                })
            else:
                print(f"Quest {quest_id} not found in Quest Catalog Service")
        except Exception as e:
            print(f"Error fetching quest details: {e}")

    return quests

# Endpoint to claim a reward (manual claim)
class ClaimRewardRequest(BaseModel):
    user_id: int
    quest_id: int

@app.post("/claim-reward/")
def claim_reward(request: ClaimRewardRequest, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    # Get user's quest progress
    cursor.execute(
        """
        SELECT times_completed, status FROM UserQuestProgress
        WHERE user_id = ? AND quest_id = ?
        """,
        (request.user_id, request.quest_id)
    )
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Quest progress not found for this user")

    times_completed, status = result

    if status != 'not_claimed':
        raise HTTPException(status_code=400, detail="No reward to claim or already claimed")

    # Update status to 'claimed'
    cursor.execute(
        """
        UPDATE UserQuestProgress
        SET status = 'claimed'
        WHERE user_id = ? AND quest_id = ?
        """,
        (request.user_id, request.quest_id)
    )
    db.commit()

    # Reward logic goes here

    return {"message": "Reward claimed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
