from datetime import date
import os
from typing import List
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from aiogram.utils.web_app import safe_parse_webapp_init_data
from app.models.User import UserModel, UserModelIn, add_user, check_in, find_by_telegram, find_by_referral
from app.models.Query import InitData
from app.db import user_collection
from app.utils import generate_invitation

player_router = APIRouter(prefix="/player")

@player_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_player_by_id(id: str) -> UserModel:
    player_response = find_by_telegram(id)
    if player_response == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'UserModel#{id} not found'
        )
    return player_response

@player_router.post("",
    status_code=status.HTTP_200_OK,
)
async def new_player(init_data: InitData):
    try:
        data = safe_parse_webapp_init_data(
            init_data=init_data.query,
            token=os.getenv("BOT_TOKEN")
        )
        data = data.model_dump()
        user = data['user']
        user['id'] = str(user['id'])
        existing_user_in_db = find_by_telegram(user["id"])
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
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Referral player not found"
                    }
                )
            new_player = add_user(user, referral_player)
            
            return new_player
        else:
            del existing_user_in_db["_id"]
            return existing_user_in_db

    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid init data"
            }
        )

@player_router.put("/checkin")
async def check_in_route(player: UserModelIn) -> UserModel:
    return check_in(player.id)