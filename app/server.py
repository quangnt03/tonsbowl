from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from app.models.Play import Play
from app.models.User import *
from app.handler.not_found import custom_404_handler
app = FastAPI()

app.add_exception_handler(StarletteHTTPException, custom_404_handler)

@app.post("/player", status_code=status.HTTP_201_CREATED)
async def new_player(new_player: User) -> User:
    new_player_response = add_user(new_player.telegram_id)
    return new_player_response

@app.put("/checkin")
async def check_in_route(player: User) -> User:
    return check_in(player.telegram_id)

@app.put("/minigame")
async def play_route(play_stat: Play) -> User:
    return play(play_stat.telegram_id, play_stat.score)

