from app.models.User import *
from app.db import farm_collection
from .User import is_existing_user
from app.models.Farm import FarmTurn
from app.handler.exceptions import *

def get_farm_turn_by_telegram(telegram_code: str):
    if not is_existing_user(telegram_code):
        raise NotFoundException(detail={ "message": "Undefined player" })
    
    farm_turn = farm_collection.find_one({
        "telegram_code": telegram_code
    }, { '_id': False }) or None

    return farm_turn

def start_farm(telegram_code: str):
    existing_farm = get_farm_turn_by_telegram(telegram_code)
    if existing_farm != None:
        raise InvalidBodyException(detail={ "message": "Player is already farming" })

    new_farm_turn = FarmTurn(telegram_code=telegram_code)

    farm_collection.insert_one({
        "telegram_code": telegram_code,
        "start_time": new_farm_turn.start_time,
        "end_time": new_farm_turn.end_time,
    })

    return new_farm_turn

