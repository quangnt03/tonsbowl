from datetime import date
from pydantic import BaseModel
from fastapi import status
from fastapi.exceptions import HTTPException
from app import constants
from app.db import user_collection

class UserModel(BaseModel):
    telegram_id: str
    sp: int = 0
    ticket: int = 0
    checkin_streak: int = 0
    last_checkin: date = str(date.today())

class UserResponse(BaseModel):
    sp: int = 0
    ticket: int = 0
    checkin_streak: int = 0
    last_checkin: date = str(date.today())


def find_by_telegram(telegram_id: str):
    user = user_collection.find_one({
        'telegram_id': telegram_id
    }) or None
    return user

def is_existing_user(telegram_id: str):
    existing_user = find_by_telegram(telegram_id)
    return existing_user != None


def add_user(telegram_id: str):
    if is_existing_user(telegram_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already registered"
        )

    added_user = UserModel(
        telegram_id=telegram_id,
        sp=10,
        ticket=1,
        checkin_streak=1,
        last_checkin=date.today().isoformat()
    )
    
    user_collection.insert_one({ 
        "telegram_id": added_user.telegram_id,
        "sp": 10,
        "ticket": 1,
        "checkin_streak": 1,
        "last_checkin": date.today().isoformat()
     })

    return added_user

def check_in(telegram_id) -> UserModel:
    existing_user = find_by_telegram(telegram_id) or None

    if existing_user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
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
        "telegram_id": telegram_id,
        "sp": sp,
        "ticket": ticket,
        "checkin_streak": streak,
        "last_checkin": date.today().isoformat()
    }

    user_collection.update_one(filter={
        "telegram_id": telegram_id 
    }, update={
        "$set": updated_user
    })
    return  UserModel(**updated_user)

def play(telegram_id: str, score: int): 
    existing_user = find_by_telegram(telegram_id) or None

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
        "telegram_id": telegram_id 
    }, update={
        "$set": existing_user
    })

    updated_user = UserModel(**existing_user)

    return updated_user