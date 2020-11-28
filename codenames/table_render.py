"""
Rendering functions for future html tables
"""

import copy
import typing as tp

from django.db.models import Sum
from django.db.models.functions import Coalesce

from .consts import get_score_str
from .models import GameResult, Group, ResultType, Team


class HtmlTableCell:
    """
    Class that stores all information to pass to html table rendering.
    """

    def __init__(self,
                 *,
                 class_: str = None,
                 classes: tp.Optional[tp.List[str]] = None,
                 content: tp.Optional[str] = None,
                 title: tp.Optional[str] = None):
        if class_ is not None and classes is not None:
            raise TypeError("please specify either class_ or classes")
        self._classes: tp.List[str] = []
        if class_ is not None:
            self._classes.append(class_)
        if classes is not None:
            self._classes = copy.deepcopy(classes)
        self.content: str = ""
        if content:
            self.content = content
        self.title: tp.Optional[str] = title

    @property
    def class_(self):
        return " ".join(self._classes)

    def __repr__(self):
        return (f"HtmlTableCell("
                f"class_=\"{self.class_}\", "
                f"content=\"{self.content}\","
                f"title=\"{self.title}\","
                f")"
                )

    def __str__(self):
        return f"{self.content}"


def render_result_table_header(group: Group) -> None:
    """
    TODO: stub
    """
    teams = list(Team.objects.filter(group=group))
    return [
        HtmlTableCell(class_="place_header", content="#", title="Place"),
        HtmlTableCell(class_="team_header", content="Team"),
        *[HtmlTableCell(class_="gameresult_header", content=f"{place+1}")
          for place in range(len(teams))],
        HtmlTableCell(class_="played_header", content="Played"),
        HtmlTableCell(class_="won_header", content="Won"),
        HtmlTableCell(class_="lost_header", content="Lost"),
        HtmlTableCell(class_="wd_header", content="+/−",
                      title="Words difference"),
        HtmlTableCell(class_="fouls_header", content="Fouls"),
    ]


def get_gameresult_cell(game_result: GameResult,
                        *,
                        words_difference: tp.List[int],
                        is_team_home: bool) -> HtmlTableCell:
    """
    words_difference is in AND out!
    """
    title: tp.Optional[str] = None
    if not game_result.is_finished:
        return HtmlTableCell(
            classes=["scheduled"],
            content=game_result.schedule,
            title="Game haven't finished yet"
        )

    if game_result.result_type.is_auto:
        title = game_result.result_type.description

    classes: tp.List[str] = ["gameresult_cell"]
    if game_result.result_type.is_home_win == is_team_home:
        # Win
        if game_result.result_type.is_auto:
            # Do not count auto_win wd
            classes.append("auto_win")
        else:
            words_difference[0] += game_result.absolute_score
    else:
        # Lose
        if game_result.result_type.is_auto:
            classes.append("auto_lose")
        # Do count auto lose wd!
        words_difference[0] -= game_result.absolute_score

    return HtmlTableCell(
        classes=classes,
        content=get_score_str(
            game_result.home_score if is_team_home else game_result.away_score
        ),
        title=title)


def count_game_results(home_finished_games,
                       away_finished_games) -> tp.Tuple[int, int]:
    """
    :return: Tuple (won_count, lost_count)
    """
    home_win_result_types = ResultType.objects.filter(is_home_win=True)
    away_win_result_types = ResultType.objects.filter(is_home_win=False)

    home_wins = home_finished_games.filter(
        result_type__in=home_win_result_types)
    away_wins = away_finished_games.filter(
        result_type__in=away_win_result_types)
    home_loses = home_finished_games.filter(
        result_type__in=away_win_result_types)
    away_loses = away_finished_games.filter(
        result_type__in=home_win_result_types)

    return (home_wins.count() + away_wins.count(),
            home_loses.count() + away_loses.count())


def count_fouls(home_finished_games, away_finished_games) -> int:
    home_fouls: int = home_finished_games.aggregate(
        fouls=Coalesce(Sum("home_team_fouls"), 0)
    )["fouls"]
    away_fouls: int = away_finished_games.aggregate(
        fouls=Coalesce(Sum("away_team_fouls"), 0)
    )["fouls"]

    return home_fouls + away_fouls


def get_row(seed, team, group, num_teams):
    result_subrow: tp.List[HtmlTableCell] = [
        HtmlTableCell(
            class_=("itself_cell" if seed == rival_seed else None)
        ) for rival_seed in range(num_teams)
    ]

    home_games = GameResult.objects.filter(home_team=team, group=group)
    away_games = GameResult.objects.filter(away_team=team, group=group)

    words_difference: tp.List[int] = [0]

    # TODO: process game results that are not is_finished
    for game in home_games:
        rival_seed = game.away_team.seed
        result_subrow[rival_seed] = get_gameresult_cell(
            game,
            is_team_home=True,
            words_difference=words_difference)
    for game in away_games:
        rival_seed = game.home_team.seed
        result_subrow[rival_seed] = get_gameresult_cell(
            game,
            is_team_home=False,
            words_difference=words_difference)

    games_won: int
    games_lost: int
    games_won, games_lost = count_game_results(home_games, away_games)
    games_played: int = games_won + games_lost

    num_fouls: int = count_fouls(home_games, away_games)

    return [
        HtmlTableCell(class_="place_cell", content=f"{seed + 1}"),
        HtmlTableCell(class_="team_cell", content=f"{team.short}"),
        *result_subrow,
        HtmlTableCell(class_="played_cell", content=f"{games_played}"),
        HtmlTableCell(class_="won_cell", content=f"{games_won}"),
        HtmlTableCell(class_="lost_cell", content=f"{games_lost}"),
        HtmlTableCell(
            class_="wd_cell",
            content=f"{words_difference[0]: }",
            title="Words difference"),  # TODO: add wd getting
        # TODO: add fouls getting
        HtmlTableCell(class_="fouls_cell", content=f"{num_fouls}"),
    ]


def render_result_table_content(group: Group) -> None:
    """
    TODO: stub
    """
    teams_set = Team.objects.filter(group=group)
    num_teams = len(teams_set)
    teams = {
        item["seed"]: teams_set.get(seed=item["seed"])
        for item in teams_set.values("seed")
    }

    result_table = [None for seed in range(num_teams)]
    for seed in range(num_teams):
        team = teams[seed]
        result_table[seed] = get_row(seed, team, group, num_teams)
    return result_table
