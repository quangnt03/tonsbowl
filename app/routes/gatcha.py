from fastapi import APIRouter
from app.db import inventory_collection, user_collection
from app.models.User import UserModelInID
from app.controller.User import find_by_telegram
from app.utils.gatcha import pick_gatcha_item
from app.handler.exceptions import *
from app.data.gatcha_items import GATCHA_ITEMS
from app.data.constants import *

gatcha_router = APIRouter(prefix="/gatcha")

@gatcha_router.post('')
def gatcha_rolling(player: UserModelInID):
    existing_player = find_by_telegram(player.telegram_code)
    if existing_player == None:
        raise InvalidBodyException({
            "message": "Player does not exist"
        })
    if existing_player['sp'] < GATCHA_REQUIRED_SP:
        raise InvalidBodyException({
            "message": "Insufficient sp to gatcha"
        })
    player_inventory = inventory_collection.find_one({
        "telegram_code": player.telegram_code
    })
    gatcha_drop_item = pick_gatcha_item(GATCHA_ITEMS)

    if player_inventory == None:
        inventory_collection.insert_one({
            "telegram_code": player.telegram_code,
            "items": [{ 
                "id": gatcha_drop_item["id"], "quantity": 1 
            }]
        })
    else:
        found = False
        items = player_inventory['items']
        for (id, item) in enumerate(items):
            if item['id'] == gatcha_drop_item["id"]:
                items[id]["quantity"] += 1
                found = True
                break

        if not found:
            player_inventory['items'].append({ 
                "id": gatcha_drop_item["id"],
                "quantity": 1 
            })

            
        inventory_collection.update_one({
            "telegram_code": player.telegram_code
        }, update={
            "$set": { "items": items }
        })

    user_collection.update_one({
        "telegram_code": player.telegram_code,
    }, update={
        "$inc": { "sp": -1 * GATCHA_REQUIRED_SP }
    })
    user = find_by_telegram(player.telegram_code)
    return {
        "status_code": "200",
        "item_id": gatcha_drop_item["id"],
        "sp": user['sp']
    }

@gatcha_router.post('/inventory')
def gatcha_rolling(player: UserModelInID):
    existing_player = find_by_telegram(player.telegram_code)
    if existing_player == None:
        raise InvalidBodyException({
            "message": "Player does not exist"
        })
    player_inventory = inventory_collection.find_one({
        "telegram_code": player.telegram_code
    })
    inventory = []
    if player_inventory == None:
        inventory_collection.insert_one({
            "telegram_code": player.telegram_code,
            "items": []
        })
    else:
        inventory = player_inventory['items']    
    return {
        "status_code": "200",
        "inventory": inventory
    }