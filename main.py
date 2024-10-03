import sqlite3
from fastapi import FastAPI

# SQLite database connection
conn = sqlite3.connect("rewards_system.db")
cursor = conn.cursor()

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


from fastapi.responses import JSONResponse
from sqlite3 import IntegrityError


@app.post("/users/")
def create_user(user_name: str, status: int):
    try:
        cursor.execute(
            "INSERT INTO Users (user_name, status) VALUES (?, ?)", (user_name, status)
        )
        conn.commit()
        return {"message": "User created successfully"}
    except IntegrityError as e:
        return JSONResponse(
            status_code=400, content={"message": "Integrity error: " + str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": "Internal server error: " + str(e)}
        )

@app.post("/quests/")
def create_quest(
    reward_id: int,
    auto_claim: bool,
    streak: int,
    duplication: int,
    name: str,
    description: str,
):
    cursor.execute(
        """
    INSERT INTO Quests (reward_id, auto_claim, streak, duplication, name, description)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
        (reward_id, auto_claim, streak, duplication, name, description),
    )
    conn.commit()
    return {"message": "Quest created successfully"}


@app.post("/rewards/")
def create_reward(reward_name: str, reward_item: str, reward_qty: int):
    cursor.execute(
        """
    INSERT INTO Rewards (reward_name, reward_item, reward_qty)
    VALUES (?, ?, ?)
    """,
        (reward_name, reward_item, reward_qty),
    )
    conn.commit()
    return {"message": "Reward created successfully"}


@app.post("/user-quest-rewards/")
def create_user_quest_reward(user_id: int, quest_id: int, status: str):
    cursor.execute(
        """
    INSERT INTO User_Quest_Rewards (user_id, quest_id, status)
    VALUES (?, ?, ?)
    """,
        (user_id, quest_id, status),
    )
    conn.commit()
    return {"message": "User quest reward created successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
