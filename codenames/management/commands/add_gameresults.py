"""
Console command to add empty game results for some group.
"""

import json
import os

from django.core.management.base import BaseCommand, CommandError

from codenames.consts import CURRENT_CUP_NUMBER
from codenames.models import Arena, GameResult, Group, Team


def assert_correct_teams_seeds(teams) -> None:
    teams_seeds = set()
    for team in teams:
        if team.seed is None:
            raise CommandError(f"team {team} has no seed in group")
        if team.seed in teams_seeds:
            raise CommandError(f"More than one team with seed {team.seed}")
        teams_seeds.add(team.seed)


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
        parser.add_argument(
            "-n", "--num_teams",
            required=True,
            action="store",
            type=int,
        )

    def handle(self, *args, **options):
        try:
            dst_group: Group = Group.objects.get(
                name=options["to_group"],
                cup__number=options["cup_number"]
            )
        except Group.DoesNotExist as group_no_exist:
            raise CommandError(
                f"There is no group {options['to_group']} "
                f"on cup {options['cup_number']}"
            ) from group_no_exist

        group_size: int = options["num_teams"]

        group_teams = Team.objects.filter(group=dst_group)
        if group_teams.count() != group_size:
            raise CommandError(
                f"{group_size} teams expected, got {group_teams.count()}")

        try:
            assert_correct_teams_seeds(group_teams)
        except CommandError as command_error:
            raise command_error

        schedule_path = os.path.join(
            options["schedule_json_folder"],
            f"schedule_{(group_size + 1) // 2 * 2}.json"
        )

        with open(schedule_path, "r", encoding="utf-8") as json_src:
            schedule = json.load(json_src)

        for round_index in range(len(schedule)):
            round_games = schedule[f"{round_index + 1}"]

            # TODO: add checking already existing game results
            for game in round_games:
                try:
                    # Skip this game if group size is odd
                    # And team skips this rounds
                    # (equals "team plays with dummy team")
                    game_result = GameResult(
                        group=dst_group,
                        home_team=group_teams.get(seed=game["first"] - 1),
                        away_team=group_teams.get(seed=game["second"] - 1),
                        round_number=round_index,
                        arena=Arena.objects.filter(group=dst_group).order_by(
                            "number")[game["seat"] - 1]
                    )
                    game_result.save()
                    print(f"GameResult {game_result} saved")
                except Team.DoesNotExist:
                    continue
