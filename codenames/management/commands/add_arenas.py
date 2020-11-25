from django.core.management.base import BaseCommand, CommandError
from codenames.consts import CURRENT_CUP_NUMBER
from codenames.models import Arena, Group


class Command(BaseCommand):
    help = "Add arenas"

    def add_arguments(self, parser):
        parser.add_argument("-g", "--group_name", type=str, required=True)
        parser.add_argument("-a", "--arena_number", type=int, required=True)

    def handle(self, *args, **options):
        group = Group.objects.get(name=options["group_name"],
                                  cup_id__number=CURRENT_CUP_NUMBER)
        params = {
            "group_id": group,
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
        self.stdout.write(f"{new_arena} saved")
