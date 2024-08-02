from datetime import date
from fastapi import status
from fastapi.exceptions import HTTPException
from app.data import constants
from app.db import user_collection, referral_collection
from app.models.User import UserModel
from app.utils import generate_invitation
from app.data.constants import *
from app.handler.exceptions import *

def find_by_telegram(telegram_code: str):
    user = user_collection.find_one({
        'telegram_code': telegram_code
    }, {'_id': False}) or None
    return user

def find_by_referral(referral_code: str):
    referral_user = user_collection.find_one({
        "invitation_code": referral_code
    }, {'_id': False})
    return referral_user

def get_all_referred_player(telegram_code: str) -> list[dict]:
    player = find_by_telegram(telegram_code)
    if player == None:
        raise NotFoundException({
            "message": "Player not found"
        })
    query = user_collection.find({ "referral": telegram_code }, { '_id': False })
    referred_players = [doc for doc in query]
    if player["referral"] != None:
        referral = find_by_telegram(player["referral"])
        referred_players.append(referral)
    return referred_players

def get_friend_bonus(telegram_code: str) -> list[dict]:
    referral_info = referral_collection.find({
        "referrer": telegram_code
    })
    referral_list = []
    for doc in referral_info:
        referree = user_collection.find_one({
            "telegram_code": doc['referree']
        })
        referral_list.append({
            "first_name": referree['first_name'],
            "last_name": referree['last_name'],
            "username": referree['username'],
            "sp": doc['sp']
        })
    return referral_list

def is_existing_user(telegram_code: str):
    existing_user = find_by_telegram(telegram_code)
    return existing_user != None

def check_in(telegram_code) -> UserModel:
    existing_user = find_by_telegram(telegram_code) or None

    if existing_user == None:
        raise NotFoundException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "User not found"
            }
        )
    
    last_checkin = date.fromisoformat(existing_user['last_checkin'])
    today = date.today()
    day_diff = (today - last_checkin).days
    if day_diff == 0:
        raise InvalidBodyException(detail={
            "message": "Just checked in today"
        })
    
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
        "telegram_code": telegram_code,
        "sp": sp,
        "ticket": ticket,
        "checkin_streak": streak,
        "last_checkin": date.today().isoformat()
    }

    user_collection.update_one(filter={
        "telegram_code": telegram_code 
    }, update={
        "$set": updated_user
    })
    return updated_user

def add_user(user: dict, referral_player: str = None):
    invitation_code, invitation_link = generate_invitation.gen_invite_link()

    new_player = {
        "telegram_code": user['telegram_code'],
        "first_name": user['first_name'],
        "last_name": user['last_name'],
        "username": user['username'],
        "sp": 10,
        "ticket": 1,
        "checkin_streak": 1,
        "last_checkin": date.today().isoformat(),
        "invitation_code": invitation_code,
        "invitation_link": invitation_link,
        "referral": referral_player
    }
    user_collection.insert_one(new_player)

    if referral_player != None:
        referral_collection.insert_one({
            "referrer": referral_player,
            "referree": user['telegram_code'],
            "sp": 0,
        })
        referrer = find_by_telegram(referral_player)
        if referrer['referral'] != None:
            referral_collection.insert_one({
                "referrer": referrer['referral'],
                "referree": user['telegram_code'],
                "sp": 0
            })  
    del new_player['_id']
    return {
        "status_code": 200,
        **new_player
    }

def play(telegram_code: str, score: int): 
    existing_user = find_by_telegram(telegram_code) or None

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
        "telegram_code": telegram_code 
    }, update={
        "$set": existing_user
    })

    first_referral_award = FIRST_REFERRAL_SHARE * score
    second_referral_award = SECOND_REFERRAL_SHARE * score
    referral = existing_user['referral']
    if referral != None:
        user_collection.update_one(
            filter={ "telegram_code": referral },
            update={
                "$inc": {
                    "sp": first_referral_award
                }
            }
        )
        referral_collection.update_one(
            filter={
                "referrer": referral,
                "referree": telegram_code,
            },
            update={
                "$inc": { "sp": first_referral_award }
            }
        )
        first_referral = find_by_telegram(referral)
        second_referral = first_referral['referral']
        if second_referral != None:
            user_collection.update_one(
                filter={ "telegram_code": second_referral },
                update={
                    "$inc": {
                        "sp": second_referral_award
                    }
                }
            )
            referral_collection.update_one(
                filter={
                    "referrer": second_referral,
                    "referree": telegram_code,
                },
                update={
                    "$inc": { "sp": second_referral_award }
                }
            )

    updated_user = UserModel(**existing_user)

    return updated_user