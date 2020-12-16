"""
Functions for calculating tiebreak values
"""
import typing as tp

from django.db.models import Sum
from django.db.models.functions import Coalesce

from .models import ResultType

# Order and weight of tie breakers in group
# Start tie breaker name with "optional"
# if tie breaker is used only when all tied teams
# finished all games with each other
TIE_BREAKERS_ORDER = [
    "won",
    "games_played",
    "optional_won_between",
    "absences",
    "serious_fouls",
    "fouls",
    "black_loses",
    "optional_black_loses_between",
    "words_difference",
    "optional_words_difference_between",
]


# Choose -1 if "more is better" (like "won"), else +1
TIE_BREAKERS_WEIGHTS = {
    "won": -1,
    "optional_won_between": -1,
    "absences": +1,
    "serious_fouls": +1,
    "fouls": +1,
    "black_loses": +1,
    "optional_black_loses_between": +1,
    "words_difference": -1,
    "optional_words_difference_between": -1,
    "games_played": -1,
}


OPTIONAL_TIE_BREAKERS = {
    "optional_won_between",
    "optional_black_loses_between",
    "optional_words_difference_between",
}


def count_game_results(home_games,
                       away_games) -> tp.Tuple[int, int]:
    """
    :return: Tuple (won_count, lost_count)
    """
    home_win_result_types = ResultType.objects.filter(is_home_win=True)
    away_win_result_types = ResultType.objects.filter(is_home_win=False)

    home_wins = home_games.filter(
        result_type__in=home_win_result_types)
    away_wins = away_games.filter(
        result_type__in=away_win_result_types)
    home_loses = home_games.filter(
        result_type__in=away_win_result_types)
    away_loses = away_games.filter(
        result_type__in=home_win_result_types)

    return (home_wins.count() + away_wins.count(),
            home_loses.count() + away_loses.count())


def count_won(home_games, away_games):
    return count_game_results(home_games, away_games)[0]


def count_games_played(home_games, away_games):
    games_won, games_lost = count_game_results(home_games, away_games)
    return games_won + games_lost


def count_absences(home_games, away_games):
    return (
        home_games.filter(result_type__abbr="A2").count()
        + away_games.filter(result_type__abbr="A1").count()
    )


def count_serious_fouls(home_games, away_games):
    return (
        home_games.filter(result_type__abbr="F2").count()
        + away_games.filter(result_type__abbr="F1").count()
    )


def count_fouls(home_finished_games, away_finished_games) -> int:
    home_fouls: int = home_finished_games.aggregate(
        fouls=Coalesce(Sum("home_team_fouls"), 0)
    )["fouls"]
    away_fouls: int = away_finished_games.aggregate(
        fouls=Coalesce(Sum("away_team_fouls"), 0)
    )["fouls"]

    return home_fouls + away_fouls


def count_black_loses(home_games, away_games):
    return (
        home_games.filter(result_type__abbr="B2").count()
        + away_games.filter(result_type__abbr="B1").count()
    )


def count_words_difference(home_games, away_games):
    words_difference: int = 0
    for game in home_games:
        if not game.is_finished:
            continue
        if game.result_type.is_home_win:
            if not game.result_type.is_auto:
                words_difference += game.absolute_score
        else:
            words_difference -= game.absolute_score
    for game in away_games:
        if not game.is_finished:
            continue
        if not game.result_type.is_home_win:
            if not game.result_type.is_auto:
                words_difference += game.absolute_score
        else:
            words_difference -= game.absolute_score

    return words_difference


# functions to calculate optional tie breakers
# that get (home_games, away_games)
tie_breaker_calculators = {
    "won": count_won,
    "games_played": count_games_played,
    "absences": count_absences,
    "serious_fouls": count_serious_fouls,
    "fouls": count_fouls,
    "black_loses": count_black_loses,
    "words_difference": count_words_difference,

    "optional_won_between": count_won,
    "optional_black_loses_between": count_black_loses,
    "optional_words_difference_between": count_words_difference,
}
