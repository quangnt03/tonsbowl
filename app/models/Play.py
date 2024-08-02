from pydantic import BaseModel

class Play(BaseModel):
    telegram_code: str
    score: float = 0.0