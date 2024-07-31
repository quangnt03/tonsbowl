from pydantic import BaseModel, Field

class InitData(BaseModel):
    query: str
    command: str = None