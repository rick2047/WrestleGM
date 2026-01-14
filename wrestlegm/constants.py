"""Shared simulation and booking constants."""

P_WEIGHT = 0.6
S_WEIGHT = 0.4
D_SCALE = 100.0
P_MIN = 0.1
P_MAX = 0.9

POP_W = 0.7
STA_W = 0.3
ALIGN_BONUS = 5.0

STAMINA_MIN_BOOKABLE = 10
STAMINA_RECOVERY_PER_SHOW = 15

RIVALRY_LEVEL_CAP = 4
RIVALRY_BONUS = 0.25
BLOWOFF_BONUS = 0.5
COOLDOWN_PENALTY = 1.0
COOLDOWN_SHOWS = 6

SHOW_MATCH_COUNT = 3
PROMO_VARIANCE = 8
SHOW_SLOT_TYPES = ("match", "promo", "match", "promo", "match")
SHOW_SLOT_COUNT = len(SHOW_SLOT_TYPES)

MATCH_CATEGORIES = {
    "singles": {"id": "singles", "name": "Singles", "size": 2},
    "triple-threat": {"id": "triple-threat", "name": "Triple Threat", "size": 3},
    "fatal-4-way": {"id": "fatal-4-way", "name": "Fatal 4-Way", "size": 4},
}
MATCH_CATEGORY_ORDER = ("singles", "triple-threat", "fatal-4-way")
