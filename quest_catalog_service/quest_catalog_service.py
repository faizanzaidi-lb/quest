from fastapi import FastAPI, HTTPException
import sqlite3

# Database Setup
DATABASE = 'quests.db'

app = FastAPI()

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create rewards table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rewards (
        reward_id INTEGER PRIMARY KEY AUTOINCREMENT,
        reward_name TEXT,
        reward_item TEXT,
        reward_qty INTEGER
    )
    ''')
    
    # Create quests table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quests (
        quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
        reward_id INTEGER,
        auto_claim BOOLEAN DEFAULT FALSE,
        streak INTEGER DEFAULT 0,
        duplication INTEGER DEFAULT 0,
        name TEXT,
        description TEXT,
        FOREIGN KEY (reward_id) REFERENCES rewards(reward_id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

@app.post("/create_quest/")
async def create_quest(name: str, description: str, reward_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO quests (reward_id, name, description) VALUES (?, ?, ?)", (reward_id, name, description))
    conn.commit()
    conn.close()

    return {"message": "Quest created", "name": name}

@app.get("/get_quest/{quest_id}")
async def get_quest(quest_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM quests WHERE quest_id = ?", (quest_id,))
    quest = cursor.fetchone()

    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")

    conn.close()
    return {"quest_id": quest[0], "reward_id": quest[1], "name": quest[5], "description": quest[6]}

@app.post("/create_reward/")
async def create_reward(reward_name: str, reward_item: str, reward_qty: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO rewards (reward_name, reward_item, reward_qty) VALUES (?, ?, ?)", (reward_name, reward_item, reward_qty))
    conn.commit()
    conn.close()

    return {"message": "Reward created", "reward_name": reward_name}

@app.get("/get_rewards/{reward_id}")
async def get_rewards(reward_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM rewards WHERE reward_id = ?", (reward_id,))
    reward = cursor.fetchone()

    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")

    conn.close()
    return {"reward_id": reward[0], "reward_name": reward[1], "reward_item": reward[2], "reward_qty": reward[3]}

@app.get("/get_quests_with_rewards/")
async def get_quests_with_rewards():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT quests.quest_id, quests.name, quests.description, rewards.reward_name, rewards.reward_item
    FROM quests
    JOIN rewards ON quests.reward_id = rewards.reward_id
    ''')
    quests_with_rewards = cursor.fetchall()

    conn.close()
    return [
        {
            "quest_id": quest[0],
            "name": quest[1],
            "description": quest[2],
            "reward_name": quest[3],
            "reward_item": quest[4]
        }
        for quest in quests_with_rewards
    ]

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
