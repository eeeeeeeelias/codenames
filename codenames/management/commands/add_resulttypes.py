from django.core.management.base import BaseCommand, CommandError
from codenames.models import ResultType

from ._game_results import RESULT_TYPES


class Command(BaseCommand):
    help = "Add const game result types"

    def handle(self, *args, **options):
        for k, rt in RESULT_TYPES.items():
            new_result_type: ResultType = ResultType(
                abbr=rt.id,
                _description=rt.description,
                is_auto=rt.is_auto,
                is_home_win=rt.is_home_win,
                _auto_score=rt.auto_score
            )
            try:
                existing_result_type = ResultType.objects.get(abbr=rt.id)
                self.stdout.write(f"Result type {existing_result_type} already exists")
                continue
            except ResultType.DoesNotExist:
                pass

            new_result_type.save()
            self.stdout.write(f"{new_result_type} saved")
