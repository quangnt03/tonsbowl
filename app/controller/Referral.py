from app.data import constants
from app.controller.User import find_by_telegram
from app.db import user_collection, referral_collection

def referral_gain(player_stat: dict, sp: float):
    first_referral_award = constants.FIRST_REFERRAL_SHARE * sp
    second_referral_award = constants.SECOND_REFERRAL_SHARE * sp
    
    referral = player_stat['referral']
    if referral != None:
        referral_collection.update_one(
            filter={
                "referrer": referral,
                "referree": player_stat["telegram_code"],
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
                    "referree": referral,
                },
                update={
                    "$inc": { "sp": second_referral_award }
                }
            )

def claim_referral(player_id: str):
    
    first_referral_award = constants.FIRST_REFERRAL_SHARE * sp
    second_referral_award = constants.SECOND_REFERRAL_SHARE * sp
    
    referral = player_stat['referral']
    if referral != None:
        user_collection.update_one(
            filter={ "telegram_code": referral },
            update={
                "$inc": {
                    "sp": first_referral_award,
                    "accumulated_sp": first_referral_award,
                }
            }
        )
        referral_collection.update_one(
            filter={
                "referrer": referral,
                "referree": player_stat["telegram_code"],
            },
            update={
                "$inc": { 
                    "sp": first_referral_award,
                    "accumulated_sp": first_referral_award
                }
            }
        )
        first_referral = find_by_telegram(referral)
        second_referral = first_referral['referral']
        if second_referral != None:
            user_collection.update_one(
                filter={ "telegram_code": second_referral },
                update={
                    "$inc": {
                        "sp": second_referral_award,
                        "accumulated_sp": second_referral_award
                    }
                }
            )
            referral_collection.update_one(
                filter={
                    "referrer": second_referral,
                    "referree": referral,
                },
                update={
                    "$inc": { "sp": second_referral_award }
                }
            )