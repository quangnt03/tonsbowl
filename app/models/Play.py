from pydantic import BaseModel

class Play(BaseModel):
    telegram_id: str
    score: int = 0