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

@game_router.get("/farm/{player}")
async def get_farm_info(player: str) -> FarmTurn:
    farm_turn = get_farm_turn_by_telegram(player)
    if farm_turn == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={ "message": "User has not started farming" }
        )
    return FarmTurn(
        telegram_id=player,
        start_time=farm_turn["start_time"],
        end_time=farm_turn["end_time"]
    )

@game_router.put("/farm")
async def start_new_farm(farm: FarmTurnIn) -> FarmTurn:
    return start_farm(farm.telegram_id)

@game_router.put("/farm/claims")
async def claims_farm(farm: FarmTurnIn):
    return claim_farm_award(farm.telegram_id)
