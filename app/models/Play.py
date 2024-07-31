from pydantic import BaseModel

class Play(BaseModel):
    id: str
    score: int = 0