from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.User import *
from app.controller.User import *
from app.handler.exceptions import *

friend_router = APIRouter(prefix="/friend", tags=["Friends and Referrals"])

@friend_router.post('')
async def list_friend(player: UserModelInID):
    existing_user = find_by_telegram(player.telegram_code)
    if existing_user == None:
        raise NotFoundException(detail={
            "message": "Player not found"
        })
    friends = get_all_referred_player(player.telegram_code)
    return JSONResponse(
        content={
            "sp": existing_user["sp"],
            "accumulated_sp": existing_user["accumulated_sp"],
            "milestone": existing_user["milestone"],
            "invitation_turn": existing_user["invitation_turn"],
            "friends": friends
        }
    )

@friend_router.post('/bonus')
async def claim_friend_bonus(player: UserModelInID):
    existing_user = find_by_telegram(player.telegram_code)
    if existing_user == None:
        raise NotFoundException(detail={
            "message": "Player not found"
        })
    friend_bonus = claim_referral(player.telegram_code)
    return JSONResponse(
        content=friend_bonus
    )
