from django.core.management.base import BaseCommand, CommandError
from codenames.consts import CURRENT_CUP_NUMBER
from codenames.models import Team
from .add_players import add_one_player
from .add_players import PLAYERS_DELIMITER

class Command(BaseCommand):
    help = "Add teams from file"

    def add_arguments(self, parser):
        parser.add_argument("--txt", required=True, type=str)
        parser.add_argument(
            "--cup_number",
            action="store",
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

    def handle(self, *args, **options):
        with open(options["txt"], "r", encoding="utf-8") as src_txt:
            for line in src_txt:
                line = line.strip()
                players = line.split(PLAYERS_DELIMITER)
                # TODO: add team add
