from datetime import date
from fastapi import status
from app.data import constants
from app.db import user_collection, referral_collection
from app.models.User import UserModel
from app.utils import generate_invitation
from app.data.constants import *
from app.handler.exceptions import *

def get_all_referred_player(telegram_code: str) -> list[dict]:    
    referral_info = referral_collection.find({
        "referrer": telegram_code
    })
    data = []
    for player in referral_info:
        del player["_id"]
        del player["referrer"]
        del player["referree_telegram"]
        data.append(player)
    return data

def get_friend_bonus(telegram_code: str) -> list[dict]:
    referral_info = referral_collection.find({
        "referrer": telegram_code
    })  
    return referral_info

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

    sp = cal_streak * constants.BASE_INCREMENT_SP
    ticket = existing_user['ticket'] + (cal_streak - 1) * constants.BASE_INCREMENT_TICKET

    user_collection.update_one(filter={
        "telegram_code": telegram_code 
    }, update={
        "$set": { 
            "ticket": ticket,
            "checkin_streak": streak,
            "last_checkin": date.today().isoformat()
        }
    })

    updated_user = gain_sp(telegram_code, sp, update_acc_sp=False)
    return updated_user

def add_user(user: dict, referral_player: dict | None = None):
    invitation_code, invitation_link = generate_invitation.gen_invite_link()
    referral = referral_player["telegram_code"] if referral_player else None
    new_player = {
        "telegram_code": user['telegram_code'],
        "first_name": user['first_name'],
        "last_name": user['last_name'],
        "username": user['username'],
        "invitation_code": invitation_code,
        "invitation_link": invitation_link,
        "referral": referral,
        **DEFAULT_STATS
    }
    user_collection.insert_one(new_player)

    if referral_player != None:
        add_referral(referral_player["telegram_code"], user)

    del new_player['_id']
    return {
        "status_code": 200,
        **new_player
    }

def start_play(telegram_code: str): 
    existing_user = find_by_telegram(telegram_code) or None

    if existing_user['ticket'] < 1:
        raise InvalidBodyException(
            detail={ "message": "Not enough ticket" }
        )
    
    existing_user['ticket'] -= 1

    user_collection.update_one(filter={
        "telegram_code": telegram_code 
    }, update={
        "$set": existing_user
    })

    return existing_user["ticket"]

def play_reward(telegram_code: str, score: int): 
    existing_user = find_by_telegram(telegram_code) or None

    if existing_user == None:
        raise InvalidBodyException(
            detail={ "message": "User not found" }
        )
    
    if score < 0 or score > 280:
        raise InvalidBodyException(
            detail={ "message": "Invalid awarding stats" }
        )

    player_stat = gain_sp(telegram_code, score, can_referral_gain=True)
    
    return player_stat

def is_existing_user(telegram_code: str):
    existing_user = find_by_telegram(telegram_code)
    return existing_user != None

def add_referral(referral: str, referree: dict):
    referral_collection.insert_one({
        "referrer": referral,
        "referree_telegram": referree['telegram_code'],
        "referree_first_name": referree['first_name'],
        "referree_last_name": referree['last_name'],
        "referree_username": referree['username'],
        "sp": 0,
    })
    player = find_by_telegram(referral)
    user_collection.update_one({
        "telegram_code": referral
    }, {
        "$set": {
            "invitation_turn": player["invitation_turn"] - 1
        }
    })

def claim_referral(telegram_id: str):
    total_bonus = 0
    for referral in referral_collection.find({ "referrer": telegram_id }):
        total_bonus += referral["sp"]

    gain_sp(telegram_id, total_bonus, can_referral_gain=True)
    
    referral_collection.update_many(
        { "referrer": telegram_id }, 
        { "$set": { "sp": 0 } }
    )

    update_user = up_milestone(telegram_id)
    
    return {
        "bonus": total_bonus,
        "sp": update_user['sp'],
        "milestone": update_user['milestone'],
        "invitation_turn": update_user["invitation_turn"]
    }

def gain_sp(telegram_code: str, score: int, can_referral_gain: bool = False, update_acc_sp = True):
    user_collection.update_one(filter={
        "telegram_code": telegram_code 
    }, update={
        "$inc": {
            'sp': score
        }
    })
    if update_acc_sp:
        user_collection.update_one(filter={
            "telegram_code": telegram_code 
        }, update={
            "$inc": {
                'accumulated_sp': score
            }
        })
    player = find_by_telegram(telegram_code)
    if can_referral_gain:
        referral_gain(player, score)
    return player

def up_milestone(telegram_code: str):
    player = find_by_telegram(telegram_code)
    current_milestone = player["milestone"]
    player["accumulated_sp"] = int(player["accumulated_sp"])
    accumulated_sp = int(player["accumulated_sp"])
    if current_milestone == MAX_MILESTONE:
        return player
    next_milestone_id = 0
    for (index, milestone) in enumerate(MILESTONE):
        if milestone['sp'] <= accumulated_sp:
            next_milestone_id = index
        else:
            break
    if next_milestone_id > player["milestone"]:
        next_milestone = MILESTONE[next_milestone_id]
        if type(next_milestone['invite_codes']) == type(1):
            player["invitation_turn"] += next_milestone['invite_codes']
        else: 
            player["invitation_turn"] = next_milestone['invites_codes']
        player["milestone"] += 1
        player["raffle_ticket"] += next_milestone['raffle_ticket']

        user_collection.update_one(
            { "telegram_code": telegram_code },
            {
                "$set": player
            }
        )
    return player

def referral_gain(player_stat: dict, sp: float):
    first_referral_award = constants.FIRST_REFERRAL_SHARE * sp
    second_referral_award = constants.SECOND_REFERRAL_SHARE * sp
    
    referral = player_stat['referral']
    if referral != None:
        referral_collection.update_one(
            filter={
                "referrer": referral,
                "referree_telegram": player_stat["telegram_code"],
            },
            update={
                "$inc": { 
                    "sp": first_referral_award
                }
            }
        )
        first_referral = find_by_telegram(referral)
        second_referral = first_referral['referral']
        if second_referral != None:
            referral_collection.update_one(
                filter={
                    "referrer": second_referral,
                    "referree_telegram": referral,
                },
                update={
                    "$inc": { "sp": second_referral_award }
                }
            )

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