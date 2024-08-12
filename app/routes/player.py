import os
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from aiogram.utils.web_app import safe_parse_webapp_init_data

from app.models.User import *
from app.models.Query import InitData
from app.controller.User import *
from app.handler.exceptions import *

player_router = APIRouter(prefix="/player")

@player_router.post("",
    status_code=status.HTTP_200_OK,
)
async def get_player_info_from_init_data(init_data: InitData):
    player = None
    try:
        data = safe_parse_webapp_init_data(
            init_data=init_data.query,
            token=os.getenv("BOT_TOKEN")
        )
        data = data.model_dump()
        user = data['user']
        user['telegram_code'] = str(user['id'])
        existing_user_in_db = find_by_telegram(user["telegram_code"])
        if existing_user_in_db == None:
            referral_player = None
            if init_data.command != "null" and init_data.command != None:
                referral = init_data.command
                referral_player = find_by_referral(init_data.command)
            else:
                referral = None
            if referral != None and referral_player == None:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "Referral player not found"
                    }
                )
            if referral_player != None \
                and (referral_player["invitation_turn"] <= 0 \
                    and referral_player["invitation_turn"] != constants.UNLIMITED):
                raise InvalidBodyException(detail={
                    "message": "Referral player has no invitation turn"
                })
            new_player = add_user(user, referral_player)
            player = new_player
        else:
            player = existing_user_in_db
        return {
            "status_code": status.HTTP_200_OK,
            **player,
            "today": date.today().isoformat()
        }

    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid init data"
            }
        )

@player_router.post("/info", status_code=status.HTTP_200_OK)
async def get_player_by_id(player: UserModelInID) -> UserModelInfo:
    player_info = find_by_telegram(player.telegram_code)
    if player_info == None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": 'User not found'
            }
        )
    return UserModelInfo(**player_info)

@player_router.post("/checkin")
async def check_in_route(player: UserModelInID):
    return check_in(player.telegram_code)
