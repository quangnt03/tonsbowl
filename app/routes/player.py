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
            if len(init_data.command.strip()) > 0 and init_data.command != "null":
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
            referral_player_id = referral_player['telegram_code'] if referral_player != None else None
            new_player = add_user(user, referral_player_id)
            return new_player
        else:
            return existing_user_in_db

    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid init data"
            }
        )

@player_router.post("/friends")
async def get_friends(player: UserModelInID):
    player_response = find_by_telegram(player.telegram_code)
    if player_response == None:
        raise NotFoundException(detail={
            "message": "Unknown Player"
        })
    friends_list = get_all_referred_player(player.telegram_code)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=friends_list
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

@player_router.post('/friendbonus')
async def friend_bonus(player: UserModelInID):
    existing_user = find_by_telegram(player.telegram_code)
    if existing_user == None:
        raise NotFoundException(detail={
            "message": "Player not found"
        })
    friend_bonus = get_friend_bonus(player.telegram_code)
    return JSONResponse(
        content=friend_bonus
    )