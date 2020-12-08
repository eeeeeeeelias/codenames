"""
Console command to add empty game results for some group.
"""

import json
import os

from datetime import datetime
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
            "--i_want",
            action="store_true"
        )

    def handle(self, *args, **options):
        if not options["i_want"]:
            print("FAIL")
            return
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

        group_games = GameResult.objects.filter(group=dst_group)
        backup_time_string = datetime.now().strftime(
            "%Y_%m_%d__%H_%M_%S")
        with open(f"backup_{backup_time_string}.txt", "w") as backup:
            for game in group_games:
                print(game, file=backup)
        os.system(f"cp db.sqlite3 db_backup_{backup_time_string}")
        group_games.update(
            score=0,
            result_type=None,
            home_team_fouls=0,
            away_team_fouls=0)
