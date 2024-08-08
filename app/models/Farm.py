from typing import Annotated
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from app.models.User import *
from app.data import constants

class FarmTurn(BaseModel):
    telegram_code: Annotated[str, Field(exclude=True)]
    start_time: str
    now: str = datetime.now().isoformat()
    end_time: str


class FarmTurnIn(BaseModel):
    telegram_code: Annotated[str, Field(exclude=True)]
