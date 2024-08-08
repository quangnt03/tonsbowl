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
    sp: float = 0
    accumulated_sp: float = 0
    ticket: int = 0
    checkin_streak: int = 0
    last_checkin: str | None = None
    invitation_turn: int
    invitation_code: str
    invitation_link: str
    referral: str | None = Field(default=None, exclude=True)
    milestone: int | str = 0
    raffle_ticket: int = 0

class UserModelInfo(BaseModel):
    sp: float
    accumulated_sp: float
    ticket: int
    invitation_turn: int

class UserModelIncreaseForDebug(BaseModel):
    telegram_code: str
    sp: float = 0
    accumulated_sp: float = 0
    ticket: int = 0
    milestone: int = 0
    invitation_turn: int = 0
    