from fastapi import APIRouter, status
from starlette.exceptions import HTTPException
from app.models.User import UserModel, add_user, check_in, find_by_telegram

player_router = APIRouter(prefix="/player")

@player_router.get("/{id}", status_code=status.HTTP_201_CREATED)
async def get_player_by_id(id: str) -> UserModel:
    player_response = find_by_telegram(id)
    if player_response == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'UserModel#{id} not found'
        )
    return player_response

@player_router.post("/", status_code=status.HTTP_201_CREATED)
async def new_player(new_player: UserModel) -> UserModel:
    new_player_response = add_user(new_player.telegram_id)
    return new_player_response

@player_router.put("/checkin")
async def check_in_route(player: UserModel) -> UserModel:
    return check_in(player.telegram_id)