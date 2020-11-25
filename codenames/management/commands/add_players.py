from django.core.management.base import BaseCommand, CommandError
from codenames.models import Player

PLAYERS_DELIMITER = " - "
NAMES_DELIMITER = " "


def add_one_player(first_name, last_name, out):
    try:
        existing_player = Player.objects.get(first_name=first_name,
                                             last_name=last_name)
    except Player.DoesNotExist:
        existing_player = None
    if existing_player is not None:
        out.write(f"Player {existing_player} already exists")
        return
    new_player = Player(first_name=first_name, last_name=last_name)
    new_player.save()
    out.write(f"{new_player} saved")


class Command(BaseCommand):
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
        with open(options["txt"], "r", encoding="utf-8") as src_txt:
            for line in src_txt:
                line = line.strip()
                if options["from_teams"]:
                    players = line.split(PLAYERS_DELIMITER)
                else:
                    players = [line]
                for player in players:
                    first_name, last_name = player.split(NAMES_DELIMITER)
                    if options["first_name_first"]:
                        first_name, last_name = last_name, first_name
                    add_one_player(first_name, last_name, self.stdout)
