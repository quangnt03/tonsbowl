from typing import Annotated
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from app.models.User import *
from app.data import constants

class FarmTurn(BaseModel):
    telegram_code: Annotated[str, Field(exclude=True)]
    start_time: datetime = datetime.now().isoformat()
    end_time: datetime = (datetime.now() + timedelta(hours=constants.FARM_DURATION)).isoformat() 


class FarmTurnIn(BaseModel):
    telegram_code: Annotated[str, Field(exclude=True)]
