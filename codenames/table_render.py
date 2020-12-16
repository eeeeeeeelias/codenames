"""
Rendering functions for future html tables
"""

import copy
import typing as tp

from .consts import get_score_str
from .models import GameResult, Group, Team
from .table_consts import TABLE_COLUMNS_AFTER_RESULTS_ORDER
from .table_consts import TABLE_COLUMNS_BEFORE_RESULTS_ORDER
from .tiebreak import TIE_BREAKERS_ORDER, TIE_BREAKERS_WEIGHTS
from .tiebreak import OPTIONAL_TIE_BREAKERS
from .tiebreak import tie_breaker_calculators


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
                        is_team_home: bool) -> HtmlTableCell:
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
            classes.append("auto_win")
    else:
        # Lose
        if game_result.result_type.is_auto:
            classes.append("auto_lose")

    return HtmlTableCell(
        classes=classes,
        content=get_score_str(
            game_result.home_score if is_team_home else game_result.away_score
        ),
        title=title)


def get_row(seed, team, group, num_teams):
    """
    Return dict of HtmlTableCell objects for one team.
    """
    home_games = GameResult.objects.filter(home_team=team, group=group)
    away_games = GameResult.objects.filter(away_team=team, group=group)

    tie_breakers = {
        tb: tie_breaker_calculators[tb](home_games, away_games)
        for tb in TIE_BREAKERS_ORDER
        if tb not in OPTIONAL_TIE_BREAKERS
    }

    result_subrow: tp.List[HtmlTableCell] = [
        HtmlTableCell(
            class_=("itself_cell" if seed == rival_seed else None)
        ) for rival_seed in range(num_teams)
    ]
    for game in home_games:
        rival_seed = game.away_team.seed
        result_subrow[rival_seed] = get_gameresult_cell(
            game,
            is_team_home=True)
    for game in away_games:
        rival_seed = game.home_team.seed
        result_subrow[rival_seed] = get_gameresult_cell(
            game,
            is_team_home=False)

    games_lost = tie_breakers["games_played"] - tie_breakers["won"]

    row = {
        cell.class_: cell for cell in [
            HtmlTableCell(class_="place_cell", content=f"{seed + 1}"),
            HtmlTableCell(class_="team_cell", content=f"{team.short}"),
            HtmlTableCell(
                class_="played_cell",
                content=f"{tie_breakers['games_played']}"),
            HtmlTableCell(
                class_="won_cell",
                content=f"{tie_breakers['won']}"),
            HtmlTableCell(
                class_="lost_cell",
                content=f"{games_lost}"),
            HtmlTableCell(
                class_="words_difference_cell",
                content=f"{tie_breakers['words_difference']: }",
                title="Words difference"),
            HtmlTableCell(
                class_="fouls_cell",
                content=f"{tie_breakers['fouls']}"),
        ]
    }

    for key in tie_breakers:
        if key in TIE_BREAKERS_ORDER:
            try:
                tie_breakers[key] *= TIE_BREAKERS_WEIGHTS[key]
            except KeyError as exception:
                raise KeyError(
                    f"no tie breaker {key} in weights") from exception
        else:
            raise KeyError(f"no tie breaker {key} in order")

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


def are_all_games_finished(games, num_teams):
    needed_games_amount = num_teams * (num_teams - 1) // 2
    return needed_games_amount == len([
        game for game in games if game.is_finished
    ])


def count_optional_tie_breaker(group: Group,
                               tie_breaker,
                               table,
                               shared_places):
    # Start counting from scratch.
    for row in table:
        row["tie_breakers"][tie_breaker] = 0
    for place in set(shared_places):
        if shared_places.count(place) == 1:
            # No need for tie breaking
            continue
        place_sharing_seeds = {
            i: row["seed"]
            for i, row in enumerate(table)
            if row["tie_breakers"]["shared_place"] == place
        }
        games = GameResult.objects.filter(
            group=group,
            home_team__seed__in=place_sharing_seeds.values(),
            away_team__seed__in=place_sharing_seeds.values(),
        )

        if not are_all_games_finished(games, len(place_sharing_seeds)):
            continue
        for idx, seed in place_sharing_seeds.items():
            tb_calculator = tie_breaker_calculators[tie_breaker]
            table[idx]["tie_breakers"][tie_breaker] = tb_calculator(
                home_games=games.filter(home_team__seed=seed),
                away_games=games.filter(away_team__seed=seed)
            )
        for row in table:
            row["tie_breakers"][tie_breaker] *= (
                TIE_BREAKERS_WEIGHTS[tie_breaker])


def calculate_places(group: Group, table):
    # Give shared_place 1 to everyone.
    for row in table:
        row["tie_breakers"]["shared_place"] = 0

    num_teams = len(table)

    tie_breaker_idx = 0
    while tie_breaker_idx < len(TIE_BREAKERS_ORDER):
        shared_places = [row["tie_breakers"]["shared_place"] for row in table]
        num_ties_before_breaking = num_teams - len(set(shared_places))

        tie_breaker = TIE_BREAKERS_ORDER[tie_breaker_idx]

        if tie_breaker in OPTIONAL_TIE_BREAKERS:
            count_optional_tie_breaker(
                group, tie_breaker, table, shared_places)

        tie_breakers = [
            "shared_place"
        ] + TIE_BREAKERS_ORDER[:tie_breaker_idx + 1]

        tie_break_values = lambda item: [
            item["tie_breakers"][tb]
            for tb in tie_breakers
        ]
        table.sort(
            key=tie_break_values,
        )

        new_shared_places = [0 for _ in range(num_teams)]
        for place in range(1, num_teams):
            previous_row = table[place - 1]
            current_row = table[place]
            if tie_break_values(previous_row) == tie_break_values(current_row):
                # Shares place with previous team.
                new_shared_places[place] = new_shared_places[place - 1]
            else:
                # Get next place.
                new_shared_places[place] = place
        for place in range(num_teams):
            table[place]["tie_breakers"][
                "shared_place"
            ] = new_shared_places[place]

        # Check if that tie breaker helps
        num_ties_after_breaking = num_teams - len(
            {row["tie_breakers"]["shared_place"] for row in table}
        )

        if num_ties_after_breaking == 0:
            break
        if tie_breaker in OPTIONAL_TIE_BREAKERS:
            # Optional tie breaker can be used more than 1 time!
            if num_ties_before_breaking > num_ties_after_breaking:
                continue
        tie_breaker_idx += 1


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
    result_table = [None for seed in range(num_teams)]
    for seed in range(num_teams):
        team = teams[seed]
        result_table[seed] = get_row(
            seed, team, group, num_teams)
    calculate_places(group, result_table)
    for row in result_table:
        row["place_cell"].content = row["tie_breakers"]["shared_place"] + 1

    return get_result_table_with_sorted_results(result_table)


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
