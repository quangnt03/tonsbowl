from typing import Annotated
from fastapi import status
from fastapi.exceptions import HTTPException
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from app.models.User import *
from app.db import farm_collection, user_collection
from app import constants
from app.models.User import is_existing_user, find_by_telegram

class FarmTurn(BaseModel):
    telegram_id: Annotated[str, Field(exclude=True)]
    start_time: datetime = datetime.now().isoformat()
    end_time: datetime = (datetime.now() + timedelta(hours=constants.FARM_DURATION)).isoformat() 


class FarmTurnIn(BaseModel):
    telegram_id: Annotated[str, Field(exclude=True)]

def get_farm_turn_by_telegram(telegram_id: str):
    if not is_existing_user(telegram_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={ "message": "Undefined player" }
        )
    
    farm_turn = farm_collection.find_one({
        "telegram_id": telegram_id
    }) or None

    return farm_turn

def start_farm(telegram_id: str):
    existing_farm = get_farm_turn_by_telegram(telegram_id)
    if existing_farm != None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player is already farming"
        )
    
    new_farm_turn = FarmTurn(telegram_id=telegram_id)

    farm_collection.insert_one({
        "telegram_id": telegram_id,
        "start_time": new_farm_turn.start_time,
        "end_time": new_farm_turn.end_time,
    })

    return new_farm_turn

