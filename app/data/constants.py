from datetime import date
UNLIMITED="unlimited"
BASE_INCREMENT_SP=10
BASE_INCREMENT_TICKET=2
MAX_STREAK=7
DEFAULT_STATS={
    "sp": 10.0,
    "accumulated_sp": 0,
    "ticket": 1,
    "checkin_streak": 1,
    "last_checkin": date.today().isoformat(),
    "invitation_turn": 1,
    "milestone": 0,
    "raffle_ticket": 0,
}
FARM_DURATION=0.05
FARM_AWARD=200
FIRST_REFERRAL_SHARE=0.1
SECOND_REFERRAL_SHARE=0.05
GATCHA_REQUIRED_SP=500
MILESTONE=[
    {"sp": 0, "invite_codes": 0, "raffle_ticket": 0},
    {"sp": 1000, "invite_codes": 1, "raffle_ticket": 0},
    {"sp": 11000, "invite_codes": 2, "raffle_ticket": 1},
    {"sp": 31000, "invite_codes": 3, "raffle_ticket": 2},
    {"sp": 81000, "invite_codes": 6, "raffle_ticket": 3},
    {"sp": 156000, "invite_codes": 10, "raffle_ticket": 4},
    {"sp": 306000, "invite_codes": "unlimited", "raffle_ticket": 5}
]
MAX_MILESTONE=6