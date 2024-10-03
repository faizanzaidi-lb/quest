from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import uuid

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory databases for user quests and rewards
user_quests_db: Dict[str, Dict] = {}


class UserQuest(BaseModel):
    user_id: str
    quest_id: str
    progress: str = "not_started"  # Default progress state
    reward: str = "none"  # Default reward state


@app.post("/user-quests")
def add_user_quest(user_quest: UserQuest):
    quest_key = f"{user_quest.user_id}_{user_quest.quest_id}"
    user_quests_db[quest_key] = user_quest.dict()
    return {"message": "User quest added", "quest_key": quest_key}


@app.get("/user-quests/{user_id}", response_model=List[Dict])
def get_user_quests(user_id: str):
    return [quest for quest in user_quests_db.values() if quest["user_id"] == user_id]


@app.get("/user-quests/{user_id}/{quest_id}")
def get_user_quest(user_id: str, quest_id: str):
    quest_key = f"{user_id}_{quest_id}"
    quest = user_quests_db.get(quest_key)
    if not quest:
        raise HTTPException(status_code=404, detail="User quest not found")
    return quest


@app.post("/user-quests/create")
def create_user_quest(user_id: str, quest_id: str):
    quest_key = f"{user_id}_{quest_id}"
    if quest_key in user_quests_db:
        return {"message": "Quest already exists for user"}
    user_quests_db[quest_key] = UserQuest(user_id=user_id, quest_id=quest_id).dict()
    return {"message": "User quest created", "quest_key": quest_key}

