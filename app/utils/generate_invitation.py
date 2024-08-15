import secrets

BASE_LINK = "https://t.me/tonbowl_bot/tonbowls?startapp="

def gen_invite_link():
    invitation_code = secrets.token_hex(4)
    invitation_link = f'{BASE_LINK}{invitation_code}'
    return [invitation_code, invitation_link]
