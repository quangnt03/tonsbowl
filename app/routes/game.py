from fastapi import APIRouter
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from app.models.Play import Play
from app.models.User import UserModel, play
from app.models.Farm import *

game_router = APIRouter(prefix="/game")

@game_router.put("/minigame")
async def play_route(play_stat: Play) -> UserModel:
    return play(play_stat.telegram_id, play_stat.score)

@game_router.get("/farm")
async def get_farm_info(player: UserModel) -> FarmTurn:
    farm_turn = get_farm_turn_by_telegram(player.telegram_id)
    return farm_turn

@game_router.put("/farm")
async def start_new_farm(farm: FarmTurn) -> FarmTurn:
    return start_farm(farm.telegram_id)

@game_router.put("/farm/claims")
async def claims_farm(farm: FarmTurn):
    return claim_farm_award(farm.telegram_id)
