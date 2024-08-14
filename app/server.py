import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException 
from fastapi.middleware.cors import CORSMiddleware
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
from app.routes import game, player, gatcha, friend
from app.models.User import UserModelIncreaseForDebug, UserModelInID
from app.db import user_collection, referral_collection, farm_collection, inventory_collection
from app.controller.User import find_by_telegram
from app.handler.not_found import custom_404_handler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return JSONResponse("Server is online", status_code=200)

app.add_exception_handler(HTTPException, custom_404_handler)
app.include_router(player.player_router)
app.include_router(game.game_router)
app.include_router(gatcha.gatcha_router)
app.include_router(friend.friend_router)

if os.getenv("ENV") == "dev":
    @app.post("/gain")
    def gain_point(player: UserModelIncreaseForDebug):
        user_collection.update_one({
            "telegram_code": player.telegram_code,
        }, {
            "$inc": {
                "sp": player.sp,
                "accumulated_sp": player.accumulated_sp,
                "ticket": player.ticket,
                "milestone": player.milestone,
                "invitation_turn": player.invitation_turn
            }
        })
        user = find_by_telegram(player.telegram_code)
        return user
        
    @app.post("/remove")
    def remove_player(player: UserModelInID):
        user_collection.delete_one({ "telegram_code": player.telegram_code })
        referral_collection.delete_one({ "referrer": player.telegram_code })
        farm_collection.delete_one({ "telegram_code": player.telegram_code })
        inventory_collection.delete_one({ "telegram_code": player.telegram_code })
        
        return {
            "telegram_code": player.telegram_code,
            "deleted": True
        }
        