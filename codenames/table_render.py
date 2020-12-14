"""
Rendering functions for future html tables
"""

import copy
import typing as tp

from django.db.models import Sum
from django.db.models.functions import Coalesce

from .consts import get_score_str
from .models import GameResult, Group, ResultType, Team
from .table_consts import TABLE_COLUMNS_AFTER_RESULTS_ORDER
from .table_consts import TABLE_COLUMNS_BEFORE_RESULTS_ORDER
from .table_consts import TIE_BREAKERS_ORDER, TIE_BREAKERS_WEIGHTS
from .table_consts import OPTIONAL_TIE_BREAKERS


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
    group_size = Team.objects.filter(group=group).count()
    header_row = {
        cell.class_: cell for cell in [
            HtmlTableCell(class_="place_header", content="#", title="Place"),
            HtmlTableCell(class_="team_header", content="Team"),
            HtmlTableCell(class_="played_header", content="Played"),
            HtmlTableCell(class_="won_header", content="Won"),
            HtmlTableCell(class_="lost_header", content="Lost"),
            HtmlTableCell(class_="words_difference_header", content="+/−",
                          title="Words difference"),
            HtmlTableCell(class_="fouls_header", content="Fouls"),
        ]
    }
    return [
        header_row[f"{column}_header"]
        for column in TABLE_COLUMNS_BEFORE_RESULTS_ORDER
    ] + [
        HtmlTableCell(class_="gameresult_header", content=f"{place + 1}")
        for place in range(group_size)
    ] + [
        header_row[f"{column}_header"]
        for column in TABLE_COLUMNS_AFTER_RESULTS_ORDER
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
            content=game_result.scheduled_short,
            title="Game haven't finished yet"
        )

    if game_result.result_type.is_auto:
        title = game_result.result_type.description

    classes: tp.List[str] = ["gameresult_cell"]
    if game_result.result_type.is_home_win == is_team_home:
        # Win
        if game_result.result_type.is_auto:
            # Do not count auto_win words difference
            classes.append("auto_win")
        else:
            words_difference[0] += game_result.absolute_score
    else:
        # Lose
        if game_result.result_type.is_auto:
            classes.append("auto_lose")
        # Do count auto lose words difference!
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
    """
    Return dict of HtmlTableCell objects for one team.
    """
    home_games = GameResult.objects.filter(home_team=team, group=group)
    away_games = GameResult.objects.filter(away_team=team, group=group)

    games_won, games_lost = count_game_results(home_games, away_games)

    num_fouls: int = count_fouls(home_games, away_games)

    tie_breakers = {}
    tie_breakers["won"] = games_won
    tie_breakers["absences"] = (
        home_games.filter(result_type__abbr="A2").count()
        + away_games.filter(result_type__abbr="A1").count()
    )
    tie_breakers["serious_fouls"] = (
        home_games.filter(result_type__abbr="F2").count()
        + away_games.filter(result_type__abbr="F1").count()
    )
    tie_breakers["fouls"] = num_fouls
    tie_breakers["black_loses"] = (
        home_games.filter(result_type__abbr="B2").count()
        + away_games.filter(result_type__abbr="B1").count()
    )

    words_difference: tp.List[int] = [0]

    result_subrow: tp.List[HtmlTableCell] = [
        HtmlTableCell(
            class_=("itself_cell" if seed == rival_seed else None)
        ) for rival_seed in range(num_teams)
    ]
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

    tie_breakers["words_difference"] = words_difference[0]
    tie_breakers["games_played"] = games_won + games_lost
    tie_breakers["seed"] = seed

    for key in tie_breakers:
        tie_breakers[key] *= TIE_BREAKERS_WEIGHTS[key]

    row = {
        cell.class_: cell for cell in [
            HtmlTableCell(class_="place_cell", content=f"{seed + 1}"),
            HtmlTableCell(class_="team_cell", content=f"{team.short}"),
            HtmlTableCell(class_="played_cell",
                          content=f"{games_won + games_lost}"),
            HtmlTableCell(class_="won_cell", content=f"{games_won}"),
            HtmlTableCell(class_="lost_cell", content=f"{games_lost}"),
            HtmlTableCell(
                class_="words_difference_cell",
                content=f"{words_difference[0]: }",
                title="Words difference"),
            HtmlTableCell(class_="fouls_cell", content=f"{num_fouls}"),
        ]
    }
    row["results"] = result_subrow
    row["tie_breakers"] = tie_breakers
    row["seed"] = seed
    return row


def get_result_table_with_sorted_results(table):
    num_teams = len(table)
    sorted_table = [None for seed in range(num_teams)]
    for place, team_row in enumerate(table):
        unsorted_results = team_row["results"]
        sorted_results = [None for place in range(num_teams)]
        for rival_place, rival_row in enumerate(table):
            sorted_results[rival_place] = unsorted_results[rival_row["seed"]]
        sorted_table[place] = (
            [
                team_row[f"{column}_cell"]
                for column in TABLE_COLUMNS_BEFORE_RESULTS_ORDER
            ] + sorted_results
            + [
                team_row[f"{column}_cell"]
                for column in TABLE_COLUMNS_AFTER_RESULTS_ORDER
            ]
        )
    return sorted_table


def sort_result_table(table):
    table.sort(
        key=lambda item: [
            item["tie_breakers"][tb]
            for tb in TIE_BREAKERS_ORDER
            if tb not in OPTIONAL_TIE_BREAKERS
        ],
        reverse=True
    )
    num_teams = len(table)
    for place in range(num_teams):
        table[place]["place_cell"].content = place + 1


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

    # TODO: add getting of optional tie breakers
    # like "optional_won_between",
    # "optional_black_loses_between",
    # "optional_words_difference_between".
    table_with_unsorted_results = [None for seed in range(num_teams)]
    for seed in range(num_teams):
        team = teams[seed]
        table_with_unsorted_results[seed] = get_row(
            seed, team, group, num_teams)
    sort_result_table(table_with_unsorted_results)

    return get_result_table_with_sorted_results(table_with_unsorted_results)


# Number of rounds to show in "recent" and "upcoming"
NUM_UPCOMING_ROUNDS: int = 2
NUM_RECENT_ROUNDS: int = 2

RoundSchedule = tp.Tuple[int, tp.List[GameResult]]


def get_upcoming_games_schedule(
        group: Group) -> tp.List[RoundSchedule]:
    scheduled_group_games = [
        gr for gr in GameResult.objects.filter(group=group)
        if not gr.is_finished
    ]
    upcoming_rounds_numbers: tp.List[int] = sorted(
        {gr.round_number for gr in scheduled_group_games}
    )[:NUM_UPCOMING_ROUNDS]

    upcoming_games_schedule: tp.List[RoundSchedule] = []
    for round_number in upcoming_rounds_numbers:
        round_upcoming_games = sorted(
            [
                gr for gr in scheduled_group_games
                if gr.round_number == round_number
            ],
            key=lambda game: game.arena.short
        )
        upcoming_games_schedule.append(
            (f"{round_number + 1}", round_upcoming_games)
        )

    return upcoming_games_schedule


def get_recent_games_schedule(
        group: Group) -> tp.List[RoundSchedule]:
    finished_group_games = [
        gr for gr in GameResult.objects.filter(group=group)
        if gr.is_finished
    ]
    recent_rounds_numbers: tp.List[int] = sorted(
        {gr.round_number for gr in finished_group_games}
    )[::-1][:NUM_RECENT_ROUNDS]

    recent_games_schedule: tp.List[RoundSchedule] = []
    for round_number in recent_rounds_numbers:
        round_finished_games = sorted(
            [
                gr for gr in finished_group_games
                if gr.round_number == round_number
            ],
            key=lambda game: game.arena.short
        )
        recent_games_schedule.append(
            (f"{round_number + 1}", round_finished_games)
        )

    return recent_games_schedule
