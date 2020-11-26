"""
Console command to add players to db.
"""

import typing as tp

from django.core.management.base import BaseCommand
from codenames.models import Player

PLAYERS_DELIMITER = " - "
NAMES_DELIMITER = " "


NORMAL_OUTPUT_VERBOSITY: int = 1


def add_one_player(player_line: str,
                   *,
                   out: tp.TextIO,
                   first_name_first: bool,
                   verbosity: int = NORMAL_OUTPUT_VERBOSITY
                   ) -> Player:
    first_name, last_name = player_line.split(NAMES_DELIMITER)
    if first_name_first:
        first_name, last_name = last_name, first_name

    try:
        existing_player: Player = Player.objects.get(first_name=first_name,
                                                     last_name=last_name)
        if verbosity > NORMAL_OUTPUT_VERBOSITY:
            out.write(f"Player {existing_player} already exists")
        return existing_player
    except Player.DoesNotExist:
        pass

    new_player: Player = Player(first_name=first_name, last_name=last_name)
    new_player.save()
    out.write(f"Player {new_player} saved")
    return new_player


class Command(BaseCommand):
    """
    :usage: manage.py add_players
    """
    help = "Add players from file"

    def add_arguments(self, parser):
        parser.add_argument("--txt", required=True, type=str)
        # TODO: add csv read
        parser.add_argument(
            "-f", "--first_name_first",
            action="store_true",
            help="Use if names are written like Ivan Ivanov not Ivanov Ivan"
        )
        parser.add_argument(
            "-t", "--from_teams",
            action="store_true",
            help="Use if you want to add participants from teams list."
                 "Delimiter is ' - '"
        )
        parser.add_argument(
            "-d", "--players_delimiter",
            action="store",
            default=PLAYERS_DELIMITER,
            type=str,
            help="Delimiter to split players from team"
        )

    def handle(self, *args, **options):
        num_players: int = 0
        with open(options["txt"], "r", encoding="utf-8") as src_txt:
            for line in src_txt:
                line = line.strip()
                if options["from_teams"]:
                    player_lines = line.split(PLAYERS_DELIMITER)
                else:
                    player_lines = [line]
                for player_line in player_lines:
                    num_players += 1
                    add_one_player(
                        player_line,
                        out=self.stdout,
                        first_name_first=options["first_name_first"],
                        verbosity=options["verbosity"])
        self.stdout.write(f"{num_players} players processed")
