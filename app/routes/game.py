from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())
from fastapi import status
from app.db import farm_collection, user_collection
from app.data.constants import *
from app.models.Play import Play
from app.models.User import UserModelInID
from app.models.Farm import *
from app.controller.User import *
from app.controller.Farm import *

game_router = APIRouter(prefix="")

@game_router.post("/minigame/start")
async def start_game(play_stat: UserModelInID):
    ticket = start_play(play_stat.telegram_code)
    return JSONResponse(content={
        "status_code": 200,
        "ticket": ticket
    })

@game_router.post("/minigame/claim")
async def claim_fame(play_stat: Play):
    return play_reward(play_stat.telegram_code, play_stat.score)

@game_router.post("/farm")
async def get_farm_info(player: FarmTurnIn):
    farm_turn = get_farm_turn_by_telegram(player.telegram_code)
    if farm_turn == None:
        raise InvalidBodyException(
            detail={ 
                "message": "User has not started farming"
            }
        )
    
    return {
        "status_code": 200,
        "start_time": datetime.fromisoformat(farm_turn["start_time"]),
        "end_time": datetime.fromisoformat(farm_turn["end_time"]),
        "now": datetime.now().isoformat(),
    }

@game_router.post("/farm/start")
async def start_new_farm(farm: FarmTurnIn):
    farm_info = start_farm(farm.telegram_code)
    return {
        **farm_info,
        "now": datetime.now().isoformat(),
    }

@game_router.post("/farm/claim")
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
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content={
                "status_code": status.HTTP_406_NOT_ACCEPTABLE,
                "message": "Farming is not yet completed",
                "now": datetime.now().isoformat(),
                "end": end_time,
            }
        )
    else:
        player_stat = gain_sp(farm.telegram_code, FARM_AWARD, can_referral_gain=True, update_acc_sp=True)

        farm_collection.delete_one({ "telegram_code": farm.telegram_code })
        return {
            "status_code": 200,
            "sp": player_stat["sp"],
            "ticket": player_stat["ticket"],
            "time_left": "0:00"
        }
