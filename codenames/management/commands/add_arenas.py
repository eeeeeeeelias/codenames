"""
Console command to add arenas (game places) to db.
"""

from django.core.management.base import BaseCommand

from codenames.consts import CURRENT_CUP_NUMBER
from codenames.models import Arena, Group


class Command(BaseCommand):
    """
    :usage: manage.py add_arenas
    # TODO: add description
    """
    help = "Add arenas"

    def add_arguments(self, parser):
        parser.add_argument("-g", "--group_name", type=str, required=True)
        parser.add_argument("-a", "--arena_number", type=int, required=True)

    def handle(self, *args, **options):
        group = Group.objects.get(name=options["group_name"],
                                  cup__number=CURRENT_CUP_NUMBER)
        params = {
            "group": group,
            "number": options["arena_number"]
        }
        try:
            existing_arena = Arena.objects.get(**params)
        except Arena.DoesNotExist:
            existing_arena = None
        if existing_arena is not None:
            self.stdout.write(f"Arena {existing_arena} already exists")
            return
        new_arena = Arena(**params)
        new_arena.save()
        self.stdout.write(f"Arena {new_arena} saved")
