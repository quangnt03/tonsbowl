from fastapi import APIRouter
from app.models.User import UserModelInID, UserQuest
from app.controller import Quest

quest_router = APIRouter(prefix="/quest", tags=["Social quests"])

@quest_router.post("")
def get_quest(user: UserModelInID):
    return Quest.get_social_quest_status(user.telegram_code)


@quest_router.post("/complete")
def complete_quest(quest: UserQuest):
    return Quest.complete_quest(quest.telegram_code, quest.quest_id)