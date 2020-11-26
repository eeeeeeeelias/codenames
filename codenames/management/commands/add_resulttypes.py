"""
Console command to add constant result types to db.
"""

from django.core.management.base import BaseCommand
from codenames.models import ResultType

from ._game_results import RESULT_TYPES


class Command(BaseCommand):
    """
    :usage: manage.py add_resulttypes
    """
    help = "Add const game result types"

    def handle(self, *args, **options):
        for _, result_type in RESULT_TYPES.items():
            new_result_type: ResultType = ResultType(
                abbr=result_type.id,
                _description=result_type.description,
                is_auto=result_type.is_auto,
                is_home_win=result_type.is_home_win,
                _auto_score=result_type.auto_score
            )
            try:
                existing_result_type = ResultType.objects.get(
                    abbr=result_type.id)
                self.stdout.write(
                    f"Result type {existing_result_type} already exists")
                continue
            except ResultType.DoesNotExist:
                pass

            new_result_type.save()
            self.stdout.write(f"Result type {new_result_type} saved")
