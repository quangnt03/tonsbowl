from datetime import date
from typing import Annotated
from pydantic import BaseModel, Field

class UserModelInID(BaseModel):
    telegram_code: str

class UserModelIn(BaseModel):
    telegram_code: str
    referral: str | None = Field(default=None)

class UserModel(BaseModel):
    telegram_code: Annotated[str, Field(exclude=True)]
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    sp: float = 10
    accumulated_sp: float = 10
    ticket: int = 1
    checkin_streak: int = 1 
    last_checkin: str = date.today().isoformat()
    invitation_turn: int
    invitation_code: str
    invitation_link: str
    referral: str | None = Field(default=None, exclude=True)
    milestone: int = 0
    raffle_ticket: int = 0

class UserModelInfo(BaseModel):
    sp: float
    ticket: int 

class UserModelIncreaseForDebug(BaseModel):
    telegram_code: str
    sp: float = 0
    accumulated_sp: float = 0
    ticket: int = 0
    milestone: int = 0
    invitation_turn: int = 0
    