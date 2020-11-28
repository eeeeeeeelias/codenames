"""
Console command to add teams (and players contained) to db.
"""

import typing as tp

from django.core.management.base import BaseCommand
from codenames.consts import CURRENT_CUP_NUMBER
from codenames.models import Group, Player, Team
from codenames.models import get_dummy_group_id
from .add_players import add_one_player
from .add_players import PLAYERS_DELIMITER


class Command(BaseCommand):
    """
    :usage: manage.py add_teams
    """
    help = "Add teams from file"

    def add_arguments(self, parser):
        parser.add_argument("--txt", required=True, type=str)
        parser.add_argument(
            "--cup_number",
            action="store",
            default=CURRENT_CUP_NUMBER,
            type=int,
            help=f"Cup number (default = {CURRENT_CUP_NUMBER})")
        # TODO: add csv read
        parser.add_argument(
            "-f", "--first_name_first",
            action="store_true",
            help="Use if names are written like Ivan Ivanov not Ivanov Ivan"
        )
        parser.add_argument(
            "-d", "--players_delimiter",
            action="store",
            default=PLAYERS_DELIMITER,
            type=str,
            help="Delimiter to split players from team"
        )
        parser.add_argument(
            "-g", "--to_group",
            action="store",
            type=str,
            help="Group to put every team"
        )
        parser.add_argument(
            "-s", "--assign_seeds",
            action="store_true",
            help=("Choose if you want to assign group seeds"
                  "to all teams in given order")
        )

    def handle(self, *args, **options):
        with open(options["txt"], "r", encoding="utf-8") as src_txt:
            for seed, line in enumerate(src_txt):
                line = line.strip()
                player_lines = line.split(PLAYERS_DELIMITER)

                players: tp.List[Player] = []
                for player_line in player_lines:
                    players.append(
                        add_one_player(
                            player_line,
                            out=self.stdout,
                            first_name_first=options["first_name_first"],
                            verbosity=options["verbosity"]))

                team: tp.Optional[Team] = None
                is_team_new: bool = False
                this_cup_teams = Team.objects.filter(
                    cup__number=options["cup_number"])
                already_existing_teams = (this_cup_teams.filter(
                    first_player=players[0], second_player=players[1])
                    | this_cup_teams.filter(
                        first_player=players[1], second_player=players[0]))
                if already_existing_teams:
                    team = already_existing_teams.first()
                    self.stdout.write(
                        f"Team {players[0]}/{players[1]} already exists")

                if not team:
                    team = Team(first_player=players[0],
                                second_player=players[1])
                    is_team_new = True

                group: Group = Group.objects.get(id=get_dummy_group_id())
                if options["to_group"]:
                    try:
                        group = Group.objects.get(
                            name=options["to_group"],
                            cup__number=CURRENT_CUP_NUMBER)
                    except Group.DoesNotExist:
                        self.stdout.write(
                            f"Group {options['to_group']} don't exist")

                team_seed: tp.Optional[int] = None
                if options["assign_seeds"] and group.dummy:
                    self.stdout.write(
                        "Impossible to assign seed for non-existing group")
                elif options["assign_seeds"]:
                    team_seed = seed
                Team.objects.update_or_create(first_player=team.first_player,
                                              second_player=team.second_player,
                                              defaults={"group": group,
                                                        "seed": team_seed})

                if options["to_group"] and not group.dummy:
                    if options["assign_seeds"]:
                        self.stdout.write(
                            f"Team {team} saved to group {group.short} "
                            f"(seed {team_seed})")
                    else:
                        self.stdout.write(
                            f"Team {team} saved to group {group.short}")
                elif is_team_new:
                    self.stdout.write(f"Team {team} saved")
