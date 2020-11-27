"""
Rendering functions for future html tables
"""

import typing as tp

from django.forms.models import model_to_dict

from .models import GameResult, Group, ResultType, Team


class HtmlTableCell:
    def __init__(self,
                 *,
                 class_: str = None,
                 content: tp.Optional[str] = None,
                 title: tp.Optional[str] = None):
        self.content: str = ""
        if content:
            self.content = content
        self.class_: tp.Optional[str] = class_
        self.title: tp.Optional[str] = title

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

    # print(" ".join(f"{x.count()}" for x in [home_wins, home_loses, away_wins, away_loses]))

    won = home_wins.count() + away_wins.count()
    lost = home_loses.count() + away_loses.count()

    return [
        HtmlTableCell(class_="place_cell", content=f"{seed + 1}"),
        HtmlTableCell(class_="team_cell", content=f"{team.short}"),
        *[HtmlTableCell(class_="gameresult_cell", content=f"TODO")
          for place in range(num_teams)],  # TODO: add game_result getting
        HtmlTableCell(class_="played_cell", content=f"{played}"),
        HtmlTableCell(class_="won_cell", content=f"{won}"),
        HtmlTableCell(class_="lost_cell", content=f"{lost}"),
        HtmlTableCell(class_="wd_cell", content=f"TODO",
                      title="Words difference"),  # TODO: add wd getting
        HtmlTableCell(class_="fouls_cell", content=f"TODO"),  # TODO: add fouls getting
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
