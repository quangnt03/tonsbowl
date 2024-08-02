from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())
from fastapi import status
from fastapi.exceptions import HTTPException
from app.db import farm_collection, user_collection
from app.data.constants import *
from app.models.Play import Play
from app.models.User import UserModel
from app.models.Farm import *
from app.controller.User import find_by_telegram,play
from app.controller.Farm import *
from app.controller.Referral import referral_gain

game_router = APIRouter(prefix="/game")

@game_router.post("/minigame")
async def play_route(play_stat: Play) -> UserModelInfo:
    return play(play_stat.telegram_code, play_stat.score)

@game_router.post("/farm")
async def get_farm_info(player: FarmTurnIn):
    farm_turn = get_farm_turn_by_telegram(player.telegram_code)
    if farm_turn == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={ 
                "status_code": 400,
                "message": "User has not started farming"
            }
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
        "status_code": 200,
        "start_time": datetime.fromisoformat(farm_turn["start_time"]),
        "end_time": end_time,
        "time_left": formatted_time
    }

@game_router.post("/farm")
async def start_new_farm(farm: FarmTurnIn) -> FarmTurn:
    return start_farm(farm.telegram_code)

@game_router.post("/farm/claims")
async def claims_farm(farm: FarmTurnIn): 
    existing_farm = get_farm_turn_by_telegram(farm.telegram_code)
    if existing_farm == None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Player has not started farming"
            }
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
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={
                "status_code": status.HTTP_406_NOT_ACCEPTABLE,
                "message": "Farming is not yet completed",
                "time_left":  formatted_time,
                "now": datetime.now().isoformat(),
                "end": end_time,
            }
        )
    else:
        user_collection.update_one({
            "telegram_code": farm.telegram_code
        }, update={
            "$inc": {
                "sp": constants.FARM_AWARD
            }
        })
        
        player_stat = find_by_telegram(farm.telegram_code)
        referral_gain(player_stat, constants.FARM_AWARD)
        
        farm_collection.delete_one({ "telegram_code": farm.telegram_code })
        return {
            "status_code": 200,
            "sp": player_stat["sp"],
            "ticket": player_stat["ticket"],
            "time_left": "0:00"
        }
