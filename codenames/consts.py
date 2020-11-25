import typing as tp

from string import ascii_uppercase

CURRENT_CUP_NUMBER: int = 5

GROUPS_NUMBER: int = 2

Letter = str

GROUP_NAMES: tp.List[tp.Tuple[Letter, Letter]] = [
    (ascii_uppercase[i], ascii_uppercase[i])
    for i in range(GROUPS_NUMBER)]

MAX_GROUP_SIZE: int = 10

BLACK_AUTO_SCORE = 4
TIME_AUTO_SCORE = 4
SERIOUS_FOUL_AUTO_SCORE = 8
ABSENCE_AUTO_SCORE = 8

HOME_TEAM_WORDS_NUMBER: int = 9
AWAY_TEAM_WORDS_NUMBER: int = 8


def get_non_auto_score_string(score: int) -> str:
    if score >= 0:
        return f"{score}:0"
    else:
        return f"0:{-score}"


SCORE_CHOICES = [(score, get_non_auto_score_string(score))
                 for score in range(-HOME_TEAM_WORDS_NUMBER,
                                    AWAY_TEAM_WORDS_NUMBER + 1)]

MAX_ARENAS_NUMBER: int = 10

EARLY_FEE_SIZE: int = 700
LATE_FEE_SIZE: int = 900