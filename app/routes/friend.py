import os
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from aiogram.utils.web_app import safe_parse_webapp_init_data

from app.models.User import *
from app.models.Query import InitData
from app.controller.User import *
from app.handler.exceptions import *

friend_router = APIRouter(prefix="/friend")

@friend_router.post('')
async def list_friend(player: UserModelInID):
    existing_user = find_by_telegram(player.telegram_code)
    if existing_user == None:
        raise NotFoundException(detail={
            "message": "Player not found"
        })
    friend_bonus = get_friend_bonus(player.telegram_code)
    return JSONResponse(
        content={
            "sp": existing_user["sp"],
            "invitation_turn": existing_user["invitation_turn"],
            "friends": friend_bonus
        }
    )

@friend_router.post('/bonus')
async def get_friend_bonus(player: UserModelInID):
    existing_user = find_by_telegram(player.telegram_code)
    if existing_user == None:
        raise NotFoundException(detail={
            "message": "Player not found"
        })
    friend_bonus = get_friend_bonus(player.telegram_code)
    return JSONResponse(
        content={
            "sp": existing_user["sp"],
            "invitation_turn": existing_user["invitation_turn"],
            "friends": friend_bonus
        }
    )