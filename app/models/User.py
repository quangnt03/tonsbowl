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
    sp: float
    ticket: int 
    checkin_streak: int 
    last_checkin: str
    invitation_code: str
    invitation_link: str
    referral: str | None = Field(default=None, exclude=True)
