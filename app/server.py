from fastapi import FastAPI, status
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from app.models.Play import Play
from app.models.User import UserModel, add_user, check_in, play
from app.models.Farm import *
from app.handler.not_found import custom_404_handler
app = FastAPI()

app.add_exception_handler(StarletteHTTPException, custom_404_handler)

@app.post("/player", status_code=status.HTTP_201_CREATED)
async def new_player(new_player: UserModel) -> UserModel:
    new_player_response = add_user(new_player.telegram_id)
    return new_player_response

@app.put("/checkin")
async def check_in_route(player: UserModel) -> UserModel:
    return check_in(player.telegram_id)

@app.put("/minigame")
async def play_route(play_stat: Play) -> UserModel:
    return play(play_stat.telegram_id, play_stat.score)

@app.get("/farm")
async def start_new_farm(player: UserModel) -> FarmTurnResponse:
    farm_turn = get_farm_turn_by_telegram(player.telegram_id)
    return farm_turn

@app.put("/farm")
async def start_new_farm(farm: FarmTurn) -> FarmTurnResponse:
    return start_farm(farm.telegram_id)

@app.put("/farm/claims")
async def claims_farm(farm: FarmTurn):
    return claim_farm_award(farm.telegram_id)
