import typing as tp

from django.core.management.base import BaseCommand, CommandError
from codenames.consts import CURRENT_CUP_NUMBER
from codenames.models import Player, Team
from .add_players import add_one_player
from .add_players import NAMES_DELIMITER, PLAYERS_DELIMITER

class Command(BaseCommand):
    help = "Add teams from file"

    def add_arguments(self, parser):
        parser.add_argument("--txt", required=True, type=str)
        parser.add_argument(
            "--cup_number",
            action="store",
            default=CURRENT_CUP_NUMBER,
            type=int,
            help=f"Cup number (default = current cup)")
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

    def handle(self, *args, **options):
        with open(options["txt"], "r", encoding="utf-8") as src_txt:
            for line in src_txt:
                line = line.strip()
                player_lines = line.split(PLAYERS_DELIMITER)

                players: tp.List[Player] = []
                for player_line in player_lines:
                    players.append(add_one_player(player_line,
                                   out=self.stdout,
                                   first_name_first=options["first_name_first"],
                                   verbosity=options["verbosity"]))

                existing_teams = Team.objects.filter(
                    first_player=players[0],
                    second_player=players[1],
                    cup__number=options["cup_number"])
                if existing_teams:
                    self.stdout.write(
                        f"Team {players[0]}/{players[1]} already exists")
                    continue
                existing_teams = Team.objects.filter(
                    first_player=players[1],
                    second_player=players[0],
                    cup__number=options["cup_number"])
                if existing_teams:
                    self.stdout.write(
                        f"Team {players[1]}/{players[0]} already exists")
                    continue

                new_team: Team = Team(first_player=players[0],
                                      second_player=players[1])
                new_team.save()
                self.stdout.write(f"{new_team} saved")
