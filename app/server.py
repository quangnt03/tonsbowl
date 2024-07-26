from fastapi import FastAPI, Header
from starlette.exceptions import HTTPException 
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from app.models.Farm import *
from app.routes import game, player
from app.handler.not_found import custom_404_handler

app = FastAPI()

app.add_exception_handler(HTTPException, custom_404_handler)
app.include_router(player.player_router)
app.include_router(game.game_router)