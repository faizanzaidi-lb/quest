from fastapi import FastAPI, HTTPException
import sqlite3

# Database Setup
DATABASE = 'users.db'

app = FastAPI()

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT UNIQUE,
        password TEXT,
        gold INTEGER DEFAULT 0,
        diamond INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active',
        sign_in_count INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.post("/signup/")
async def signup(user_name: str, password: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (user_name, password, gold) VALUES (?, ?, ?)", (user_name, password, 20))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    finally:
        conn.close()

    return {"message": "User created", "user_name": user_name, "gold": 20}

@app.post("/login/")
async def login(user_name: str, password: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_name = ? AND password = ?", (user_name, password))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"message": "Login successful", "user_id": user[0], "user_name": user[1], "gold": user[3], "diamond": user[4]}

@app.post("/track-status/")
async def track_status(user_name: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_name = ?", (user_name,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Check the sign-in count
    sign_in_count = user[6]

    # Update sign-in count and give rewards if applicable
    cursor.execute("UPDATE users SET sign_in_count = sign_in_count + 1 WHERE user_name = ?", (user_name,))
    conn.commit()

    # Reward logic for diamonds
    if sign_in_count == 2:  # After the third sign-in
        cursor.execute("UPDATE users SET diamond = diamond + 10 WHERE user_name = ?", (user_name,))
        conn.commit()

    cursor.execute("SELECT diamond, gold, sign_in_count FROM users WHERE user_name = ?", (user_name,))
    updated_user = cursor.fetchone()

    return {
        "message": "Track Status successful",
        "user_id": user[0],
        "user_name": user[1],
        "diamond": updated_user[0],
        "gold": updated_user[1],
        "sign_in_count": updated_user[2],
    }

@app.post("/logout/")
async def logout(user_name: str, password: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_name = ? AND password = ?", (user_name, password))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"message": f"User {user_name} logged out successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
