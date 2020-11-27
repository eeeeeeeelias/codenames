"""
Rendering functions for future html tables
"""

import copy
import typing as tp

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.forms.models import model_to_dict

from .consts import get_score_str
from .models import GameResult, Group, ResultType, Team


class HtmlTableCell:
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


def get_row(seed, team, group, num_teams):
    home_games = GameResult.objects.filter(home_team=team, group=group)
    away_games = GameResult.objects.filter(away_team=team, group=group)

    home_win_result_types = ResultType.objects.filter(is_home_win=True)
    away_win_result_types = ResultType.objects.filter(is_home_win=False)
    played: int = home_games.count() + away_games.count()

    home_wins = home_games.filter(result_type__in=home_win_result_types)
    away_wins = away_games.filter(result_type__in=away_win_result_types)
    home_loses = home_games.filter(result_type__in=away_win_result_types)
    away_loses = away_games.filter(result_type__in=home_win_result_types)

    result_subrow: tp.List[HtmlTableCell] = [
        HtmlTableCell(
            class_=("itself_cell" if seed == rival_seed else None)
        ) for rival_seed in range(num_teams)
    ]

    words_difference: tp.List[int] = [0,]

    # TODO: process game results that are not is_finished
    for hg in home_games:
        rival_seed = hg.away_team.seed
        result_subrow[rival_seed] = get_gameresult_cell(
            hg,
            is_team_home=True,
            words_difference=words_difference)
    for ag in away_games:
        rival_seed = ag.home_team.seed
        result_subrow[rival_seed] = get_gameresult_cell(
            ag,
            is_team_home=False,
            words_difference=words_difference)

    won = home_wins.count() + away_wins.count()
    lost = home_loses.count() + away_loses.count()

    home_fouls: int = home_games.aggregate(
        fouls=Coalesce(Sum("home_team_fouls"), 0)
    )["fouls"]
    away_fouls: int = away_games.aggregate(
        fouls=Coalesce(Sum("away_team_fouls"), 0)
    )["fouls"]
    fouls: int = home_fouls + away_fouls

    return [
        HtmlTableCell(class_="place_cell", content=f"{seed + 1}"),
        HtmlTableCell(class_="team_cell", content=f"{team.short}"),
        *result_subrow,
        HtmlTableCell(class_="played_cell", content=f"{played}"),
        HtmlTableCell(class_="won_cell", content=f"{won}"),
        HtmlTableCell(class_="lost_cell", content=f"{lost}"),
        HtmlTableCell(
            class_="wd_cell",
            content=f"{words_difference[0]:+}".replace("+0", "0"),
            title="Words difference"),  # TODO: add wd getting
        # TODO: add fouls getting
        HtmlTableCell(class_="fouls_cell", content=f"{fouls}"),
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
