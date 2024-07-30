import secrets

BASE_LINK = "https://t.me/tonbowl_bot"

def gen_invite_link():
    invitation_code = secrets.token_hex(4)
    invitation_link = f'{BASE_LINK}/?ref={invitation_code}'
    return [invitation_code, invitation_link]