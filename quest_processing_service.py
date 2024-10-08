import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_SERVICE_ADD_DIAMONDS_URL = "http://localhost:8001/add-diamonds/{user_id}/"


def get_db():
    conn = sqlite3.connect("quest_processing.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect("quest_processing.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS User_Quest_Rewards (
            user_id INTEGER,
            quest_id INTEGER,
            status TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, quest_id)
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


class AssignQuest(BaseModel):
    user_id: int
    quest_id: int


class UserQuestReward(BaseModel):
    user_id: int
    quest_id: int
    status: str
    progress: int


class TrackSignIn(BaseModel):
    user_id: int


@app.post("/assign-quest/")
def assign_quest(assign_quest: AssignQuest, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO User_Quest_Rewards (user_id, quest_id, status, progress)
            VALUES (?, ?, ?, ?)
            """,
            (assign_quest.user_id, assign_quest.quest_id, "in_progress", 0),
        )
        db.commit()
        return {"message": "Quest assigned successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Quest already assigned to user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user-quests/{user_id}/", response_model=List[UserQuestReward])
def get_user_quests(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT quest_id, status, progress FROM User_Quest_Rewards WHERE user_id = ?
        """,
        (user_id,),
    )
    user_quests = cursor.fetchall()
    return [
        {
            "user_id": user_id,
            "quest_id": quest[0],
            "status": quest[1],
            "progress": quest[2],
        }
        for quest in user_quests
    ]


@app.post("/complete-quest/")
def complete_quest(assign_quest: AssignQuest, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE User_Quest_Rewards
            SET status = ?, progress = ?
            WHERE user_id = ? AND quest_id = ?
            """,
            ("claimed", 3, assign_quest.user_id, assign_quest.quest_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Quest assignment not found")
        db.commit()
        return {"message": "Quest completed and reward claimed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/track-sign-in/")
def track_sign_in(data: TrackSignIn, db: sqlite3.Connection = Depends(get_db)):
    user_id = data.user_id
    quest_id = 1
    cursor = db.cursor()
    cursor.execute(
        "SELECT progress, status FROM User_Quest_Rewards WHERE user_id = ? AND quest_id = ?",
        (user_id, quest_id),
    )
    result = cursor.fetchone()
    if result:
        progress, status = result
        if status == "claimed":
            return {"message": "Quest already completed"}
        progress += 1
        if progress >= 3:
            cursor.execute(
                """
                UPDATE User_Quest_Rewards
                SET progress = ?, status = ?
                WHERE user_id = ? AND quest_id = ?
                """,
                (progress, "claimed", user_id, quest_id),
            )
            db.commit()
            reward_user(user_id, 10)
            return {"message": "Quest completed and reward claimed!"}
        else:
            cursor.execute(
                """
                UPDATE User_Quest_Rewards
                SET progress = ?
                WHERE user_id = ? AND quest_id = ?
                """,
                (progress, user_id, quest_id),
            )
            db.commit()
            return {"message": f"Progress updated to {progress}"}
    else:
        cursor.execute(
            """
            INSERT INTO User_Quest_Rewards (user_id, quest_id, status, progress)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, quest_id, "in_progress", 1),
        )
        db.commit()
        return {"message": "Quest started: 1/3 sign-ins"}


def reward_user(user_id: int, diamonds: int):
    try:
        url = AUTH_SERVICE_ADD_DIAMONDS_URL.format(user_id=user_id)
        response = requests.post(url, json={"diamonds": diamonds})
        if response.status_code != 200:
            print(f"Failed to add diamonds to user {user_id}: {response.text}")
    except Exception as e:
        print(f"Failed to reward user {user_id}: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
