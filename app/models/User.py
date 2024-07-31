from typing import Annotated, Optional
from datetime import date
from pydantic import BaseModel, Field
from fastapi import status
from fastapi.exceptions import HTTPException
from app import constants
from app.db import user_collection
from app.utils import generate_invitation

class UserModelIn(BaseModel):
    id: str
    referral: str | None = Field(default=None)

class UserModel(BaseModel):
    id: Annotated[str, Field(exclude=True)]
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    sp: int 
    ticket: int 
    checkin_streak: int 
    last_checkin: str
    invitation_code: str
    invitation_link: str
    referral: str | None = Field(default=None, exclude=True)


def find_by_telegram(id: str):
    user = user_collection.find_one({
        'id': id
    }) or None
    return user

def find_by_referral(referral_code: str):
    referral_user = user_collection.find_one({
        "invitation_code": referral_code
    })
    return referral_user

def is_existing_user(id: str):
    existing_user = find_by_telegram(id)
    return existing_user != None

def check_in(id) -> UserModel:
    existing_user = find_by_telegram(id) or None

    if existing_user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "User not found"
            }
        )
    
    last_checkin = date.fromisoformat(existing_user['last_checkin'])
    today = date.today()
    day_diff = (today - last_checkin).days
    if day_diff == 0:
        raise HTTPException(status_code=402, detail="Just checked in today")
    
    streak = 1
    if day_diff == 1:
        streak += existing_user["checkin_streak"] 

    if streak < constants.MAX_STREAK:
        cal_streak = streak
    else:
        cal_streak = constants.MAX_STREAK 

    sp = existing_user['sp'] + cal_streak * constants.BASE_INCREMENT_SP
    ticket = existing_user['ticket'] + constants.DEFAULT_TICKET + (cal_streak - 1) * constants.BASE_INCREMENT_TICKET

    updated_user = { 
        "id": id,
        "sp": sp,
        "ticket": ticket,
        "checkin_streak": streak,
        "last_checkin": date.today().isoformat()
    }

    user_collection.update_one(filter={
        "id": id 
    }, update={
        "$set": updated_user
    })
    return  UserModel(**updated_user)

def add_user(user: dict, referral_player: str = None):
    invitation_code, invitation_link = generate_invitation.gen_invite_link()

    new_player = {
        "id": user['id'],
        "first_name": user['first_name'],
        "last_name": user['last_name'],
        "username": user['username'],
        "sp": 0,
        "ticket": 1,
        "checkin_streak": 1,
        "last_checkin": date.today().isoformat(),
        "invitation_code": invitation_code,
        "invitation_link": invitation_link,
        "referral": referral_player
    }
    
    user_collection.insert_one(new_player)
    del new_player["_id"]
    
    return new_player

def play(id: str, score: int): 
    existing_user = find_by_telegram(id) or None

    if existing_user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if score < 0 or score > 280:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid awarding stat"
        )

    if existing_user['ticket'] < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient ticket to play"
        )
    
    existing_user['sp'] += score
    existing_user['ticket'] -= 1

    user_collection.update_one(filter={
        "id": id 
    }, update={
        "$set": existing_user
    })

    updated_user = UserModel(**existing_user)

    return updated_user