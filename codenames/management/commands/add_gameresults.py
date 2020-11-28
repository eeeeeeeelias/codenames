"""
Console command to add empty game results for some group.
"""

import json
import os

from django.core.management.base import BaseCommand, CommandError

from codenames.consts import CURRENT_CUP_NUMBER
from codenames.models import Arena, GameResult, Group, Team


class Command(BaseCommand):
    """
    :usage: manage.py add_gameresults
    # TODO: add description
    """
    help = "Add empty gase result for some group"

    def add_arguments(self, parser):
        parser.add_argument(
            "-g", "--to_group",
            required=True,
            action="store",
            type=str,
        )
        parser.add_argument(
            "--cup_number",
            action="store",
            default=CURRENT_CUP_NUMBER,
            type=int,
            help=f"Cup number (default = {CURRENT_CUP_NUMBER})"
        )
        parser.add_argument(
            "-d", "--schedule_json_folder",
            required=True,
            action="store",
            type=str,
        )

    def handle(self, *args, **options):
        group_size: int = 8
        rounds_number: int = (group_size
                              if group_size % 2 != 0
                              else group_size - 1)
        arenas_number: int = group_size // 2

        group_name: str = options["to_group"]
        cup_number: int = options["cup_number"]
        try:
            dst_group: Group = Group.objects.get(
                name=group_name,
                cup__number=cup_number
            )
        except Group.DoesNotExist as group_no_exist:
            raise CommandError(
                f"There is no group {group_name} on cup {cup_number}"
            ) from group_no_exist

        group_teams = Team.objects.filter(group=dst_group)
        if group_teams.count() != group_size:
            raise CommandError(
                f"{group_size} teams expected, got {group_teams.count()}")

        teams_seeds = set()
        for team in group_teams:
            if team.seed is None:
                raise CommandError(f"team {team} has no seed in group")
            if team.seed in teams_seeds:
                raise CommandError(f"More than one team with seed {team.seed}")
            teams_seeds.add(team.seed)

        group_arenas = dict(
            zip(range(arenas_number),
                Arena.objects.filter(group=dst_group).order_by("number"))
        )

        schedule_path = os.path.join(
            options["schedule_json_folder"],
            f"schedule_{(group_size + 1) // 2 * 2}.json"
        )
        with open(schedule_path, "r", encoding="utf-8") as json_src:
            schedule = json.load(json_src)
        for round in range(rounds_number):
            round_games = schedule[f"{round + 1}"]

            # TODO: add checking already existing game results
            for game in round_games:
                game_result = GameResult(
                    group=dst_group,
                    home_team=group_teams.get(seed=game["first"] - 1),
                    away_team=group_teams.get(seed=game["second"] - 1),
                    round_number=round,
                    arena=group_arenas[game["seat"] - 1]
                )
                game_result.save()
                print(f"GameResult {game_result} saved")
