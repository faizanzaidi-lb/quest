import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, quest_id)
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


class UserQuestReward(BaseModel):
    user_id: int
    quest_id: int
    status: str


@app.post("/user-quest-rewards/")
def create_user_quest_reward(
    user_quest_reward: UserQuestReward, db: sqlite3.Connection = Depends(get_db)
):
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


@app.get("/user-quests/{user_id}/")
def get_user_quests(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT quest_id, status
        FROM User_Quest_Rewards
        WHERE user_id = ?
        """,
        (user_id,),
    )
    user_quests = cursor.fetchall()
    return [
        {
            "quest_id": quest[0],
            "status": quest[1],
        }
        for quest in user_quests
    ]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
