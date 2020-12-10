"""
Consts for codenames app.
"""

import typing as tp

from string import ascii_uppercase

CURRENT_CUP_NUMBER: int = 5

GROUPS_NUMBER: int = 4

Letter = str

GROUP_NAMES: tp.List[tp.Tuple[Letter, Letter]] = [
    (ascii_uppercase[i], ascii_uppercase[i])
    for i in range(GROUPS_NUMBER)]

MAX_GROUP_SIZE: int = 10

BLACK_AUTO_SCORE = 4
TIME_AUTO_SCORE = 4
SERIOUS_FOUL_AUTO_SCORE = 8
ABSENCE_AUTO_SCORE = 8


MAX_ARENAS_NUMBER: int = 10

EARLY_FEE_SIZE: int = 700
LATE_FEE_SIZE: int = 900

DUMMY_STRING_REPRESENTATION: str = "---------"
DUMMY_GROUP_NAME: str = "Z"


def get_score_str(score: int) -> str:
    """
    Get string with scores with colon
    :param score: negative int for away win, positive int for home win
    :return: string with score
    """
    if score == 0:
        return DUMMY_STRING_REPRESENTATION
    if score > 0:
        return f"{score}:0"
    return f"0:{-score}"


HOME_TEAM_WORDS_NUMBER: int = 9
AWAY_TEAM_WORDS_NUMBER: int = 8

SCORE_CHOICES = [(score, get_score_str(score))
                 for score in range(-HOME_TEAM_WORDS_NUMBER,
                                    AWAY_TEAM_WORDS_NUMBER + 1)]
