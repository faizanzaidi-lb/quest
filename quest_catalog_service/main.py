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

# In-memory database for quests
quests_db: Dict[str, Dict] = {}


class Quest(BaseModel):
    title: str
    description: str


@app.post("/quests")
def create_quest(quest: Quest):
    quest_id = str(uuid.uuid4())
    quests_db[quest_id] = quest.dict()
    return {"message": "Quest created", "quest_id": quest_id}


@app.get("/quests", response_model=List[Dict])
def get_quests():
    return quests_db


@app.get("/quests/{quest_id}")
def get_quest(quest_id: str):
    quest = quests_db.get(quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    return quest
