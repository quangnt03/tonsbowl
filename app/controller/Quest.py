from fastapi.responses import JSONResponse
from .User import find_by_telegram, gain_sp, user_collection

def get_social_quest_status(telegram_id: str):
    user = find_by_telegram(telegram_id)
    if user is None:
        return JSONResponse(
            status_code=404,
            content={
                "status_code": 404,
                "message": 'User not found'
            }
        )
    responses = []
    for index, is_completed in enumerate(user["quests"]):
        response = {
            "quest_id": index,
            "is_completed": is_completed
        }
        responses.append(response)
    return JSONResponse(content=responses)


def complete_quest(telegram_id: str, quest_id: int):
    user = find_by_telegram(telegram_id)
    if user is None:
        return JSONResponse(
            status_code=404,
            content={
                "status_code": 404,
                "message": 'User not found'
            }
        )
    if quest_id < 0 or quest_id > 6:
        return JSONResponse(
            status_code=400,
            content={
                "status_code": 400,
                "message": 'Undefined quest'
            }
        )
    quests = user["quests"]
    if quests[quest_id]:
        return JSONResponse(
            status_code=400,
            content={
                "status_code": 400,
                "message": 'The quest is already finished'
            }
        )
    user["quests"][quest_id] = True
    
    new_user = gain_sp(telegram_id, 50, True)
    user_collection.update_one(filter={
        "telegram_code": telegram_id
    }, update={
        "$set": {
            "quests": user["quests"]
        }
    })
    
    return {
        "is_completed": True,
        "sp": new_user["sp"]
    }