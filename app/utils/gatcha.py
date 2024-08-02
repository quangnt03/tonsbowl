import random

def pick_gatcha_item(items: list[dict]) -> dict:
    flat_item_list = []
    for item in items:
        flat_item_list.extend([item] * int(item['drop_chance'] * 100))

    # Function to pick a random item based on drop rates
    return random.choice(flat_item_list)
