from datetime import datetime
from fastapi import APIRouter
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())
from fastapi import status
from fastapi.exceptions import HTTPException
from app.models.User import *
from app.db import farm_collection, user_collection
from app import constants
from app.models.User import find_by_telegram
from app.models.Play import Play
from app.models.User import UserModel, play
from app.models.Farm import *

game_router = APIRouter(prefix="/game")

@game_router.put("/minigame")
async def play_route(play_stat: Play) -> UserModel:
    return play(play_stat.id, play_stat.score)

@game_router.get("/farm/{player}")
async def get_farm_info(player: str):
    farm_turn = get_farm_turn_by_telegram(player)
    if farm_turn == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={ "message": "User has not started farming" }
        )
    end_time = datetime.fromisoformat(farm_turn["end_time"])
    time_left = (end_time - datetime.now()).total_seconds()
    hours = int(time_left // 3600)
    minutes = int((time_left % 3600) // 60)
    if minutes < 10:
        formatted_time = f"{hours}:0{minutes}"
    else:
        formatted_time = f"{hours}:{minutes}"
    return {
        "start_time": datetime.fromisoformat(farm_turn["start_time"]),
        "end_time": end_time,
        "time_left": formatted_time
    }

@game_router.put("/farm")
async def start_new_farm(farm: FarmTurnIn) -> FarmTurn:
    return start_farm(farm.id)

@game_router.put("/farm/claims")
async def claims_farm(farm: FarmTurnIn): 
    existing_farm = get_farm_turn_by_telegram(farm.id)
    if existing_farm == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player has not started farming"
        )
    end_time = existing_farm['end_time']
    end_time_iso = datetime.fromisoformat(end_time)
    time_left = end_time_iso - datetime.now()
    total_seconds = time_left.total_seconds()


    if total_seconds > 0:
        # Calculate hours and minutes
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        if minutes < 10:
            formatted_time = f"{hours}:0{minutes}"
        else:
            formatted_time = f"{hours}:{minutes}"
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={
                "error": "Farming is not yet completed",
                "time_left":  formatted_time,
                "now": datetime.now().isoformat(),
                "end": end_time,
            }
        )
    else:
        user_collection.update_one({
            "id": farm.id
        }, update={
            "$inc": {
                "sp": constants.FARM_AWARD
            }
        })
        farm_collection.delete_one({ "id": farm.id })
        player_stat = find_by_telegram(farm.id)
        return {
            "sp": player_stat["sp"],
            "ticket": player_stat["ticket"],
            "time_left": "0:00"
        }
