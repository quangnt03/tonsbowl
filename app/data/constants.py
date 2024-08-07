from datetime import date

BASE_INCREMENT_SP=10
BASE_INCREMENT_TICKET=2
MAX_STREAK=7
DEFAULT_STATS={
    "sp": 10.0,
    "accumulated_sp": 10.0,
    "ticket": 1,
    "checkin_streak": 1,
    "last_checkin": date.today().isoformat(),
    "invitation_turn": 1,
    "milestone": 0,
}
FARM_DURATION=8
FARM_AWARD=200
FIRST_REFERRAL_SHARE=0.1
SECOND_REFERRAL_SHARE=0.05
GATCHA_REQUIRED_SP=500