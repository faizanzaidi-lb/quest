from fastapi import FastAPI, HTTPException
import sqlite3

# Database Setup
DATABASE = 'quest_catalog.db'

app = FastAPI()

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT UNIQUE,
        gold INTEGER DEFAULT 0,
        diamond INTEGER DEFAULT 0,
        status TEXT CHECK(status IN ('new', 'not_new', 'banned'))
    )
    ''')
    
    # Create rewards table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rewards (
        reward_id INTEGER PRIMARY KEY AUTOINCREMENT,
        reward_name TEXT,
        reward_item TEXT CHECK(reward_item IN ('gold', 'diamond')),
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
    
    # Create user_quest_rewards table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_quest_rewards (
        user_quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        quest_id INTEGER,
        status TEXT CHECK(status IN ('claimed', 'not_claimed')),
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (quest_id) REFERENCES quests(quest_id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

@app.post("/create_quest/")
async def create_quest(name: str, description: str, reward_id: int, auto_claim: bool, streak: int, duplication: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO quests (reward_id, name, description, auto_claim, streak, duplication) VALUES (?, ?, ?, ?, ?, ?)", 
                   (reward_id, name, description, auto_claim, streak, duplication))
    conn.commit()
    conn.close()

    return {"message": "Quest created", "name": name}

@app.post("/create_reward/")
async def create_reward(reward_name: str, reward_item: str, reward_qty: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO rewards (reward_name, reward_item, reward_qty) VALUES (?, ?, ?)", (reward_name, reward_item, reward_qty))
    conn.commit()
    conn.close()

    return {"message": "Reward created", "reward_name": reward_name}

@app.post("/assign_quest_to_user/")
async def assign_quest_to_user(user_id: int, quest_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO user_quest_rewards (user_id, quest_id, status) VALUES (?, ?, 'not_claimed')", (user_id, quest_id))
    conn.commit()
    conn.close()

    return {"message": "Quest assigned to user"}

@app.get("/get_user_quests/{user_id}")
async def get_user_quests(user_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT quests.quest_id, quests.name, quests.description, user_quest_rewards.status
    FROM user_quest_rewards
    JOIN quests ON user_quest_rewards.quest_id = quests.quest_id
    WHERE user_quest_rewards.user_id = ?
    ''', (user_id,))
    
    user_quests = cursor.fetchall()

    conn.close()
    return [
        {
            "quest_id": quest[0],
            "name": quest[1],
            "description": quest[2],
            "status": quest[3]
        }
        for quest in user_quests
    ]

@app.post("/receive_reward/")
async def receive_reward(user_id: int, quest_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Update the user quest reward status to claimed manually
    cursor.execute("UPDATE user_quest_rewards SET status = 'claimed' WHERE user_id = ? AND quest_id = ?", (user_id, quest_id))
    conn.commit()
    conn.close()

    return {"message": "Reward received for the quest"}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
