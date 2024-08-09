from datetime import datetime, timedelta
from app.models.User import *
from app.db import farm_collection
from .User import is_existing_user
from app.models.Farm import FarmTurn
from app.handler.exceptions import *
from app.data import constants

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

    new_farm_turn = {
        "telegram_code":telegram_code,
        "start_time": datetime.now().isoformat(),
        "end_time":(datetime.now() + timedelta(hours=constants.FARM_DURATION)).isoformat() 
    }

    farm_collection.insert_one(new_farm_turn.copy())

    return new_farm_turn

