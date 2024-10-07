from fastapi import FastAPI, HTTPException
import sqlite3

# Database Setup
DATABASE = 'user_quest_rewards.db'

app = FastAPI()

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_quest_rewards (
        user_id INTEGER,
        quest_id INTEGER,
        status TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (quest_id) REFERENCES quests(quest_id)
    )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.post("/track_quest/")
async def track_quest(user_id: int, quest_id: int, status: str):
    if status not in ["in_progress", "completed", "failed"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO user_quest_rewards (user_id, quest_id, status) VALUES (?, ?, ?)", (user_id, quest_id, status))
        conn.commit()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

    return {"message": "Quest tracked", "user_id": user_id, "quest_id": quest_id}

@app.get("/get_user_quest_rewards/{user_id}")
async def get_user_quest_rewards(user_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_quest_rewards WHERE user_id = ?", (user_id,))
    rewards = cursor.fetchall()

    conn.close()
    return [{"user_id": reward[0], "quest_id": reward[1], "status": reward[2], "date": reward[3]} for reward in rewards]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
