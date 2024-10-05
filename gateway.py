from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

# Service URLs
USER_AUTH_SERVICE_URL = "http://localhost:8001"
QUEST_CATALOG_SERVICE_URL = "http://localhost:8002"
QUEST_PROCESSING_SERVICE_URL = "http://localhost:8003"

# Proxy endpoints for User Authentication Service
@app.post("/register")
def register(user: dict):
    response = requests.post(f"{USER_AUTH_SERVICE_URL}/register", json=user)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.json())

@app.post("/login")
def login(user: dict):
    response = requests.post(f"{USER_AUTH_SERVICE_URL}/login", json=user)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.json())

@app.get("/users")
def get_users():
    response = requests.get(f"{USER_AUTH_SERVICE_URL}/users")
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.json())

# Proxy endpoints for Quest Catalog Service
@app.get("/quests/")
def get_quests():
    response = requests.get(f"{QUEST_CATALOG_SERVICE_URL}/quests/")
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.json())

@app.get("/quests/{quest_id}")
def get_quest(quest_id: int):
    response = requests.get(f"{QUEST_CATALOG_SERVICE_URL}/quests/{quest_id}")
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.json())

# Proxy endpoints for Quest Processing Service
@app.post("/track-login/")
def track_login(event: dict):
    response = requests.post(f"{QUEST_PROCESSING_SERVICE_URL}/track-login/", json=event)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.json())

@app.get("/user-quests/{user_id}")
def get_user_quests(user_id: int):
    response = requests.get(f"{QUEST_PROCESSING_SERVICE_URL}/user-quests/{user_id}")
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.json())

@app.post("/claim-reward/")
def claim_reward(user_id: int, quest_id: int):
    response = requests.post(f"{QUEST_PROCESSING_SERVICE_URL}/claim-reward/", json={"user_id": user_id, "quest_id": quest_id})
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.json())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
