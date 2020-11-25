"""
Views for codenames app.
"""

from django.shortcuts import render

from .consts import CURRENT_CUP_NUMBER
from .models import Group


def start_view(request):
    """
    Start view of tounament website.
    """
    groups = [g.name for g in Group.objects.filter(
        cup_id__number=CURRENT_CUP_NUMBER)]
    context = {
        "group_names": groups
    }
    return render(request, "codenames/start_page.html", context)


def all_groups_tables_view(request):
    """
    View with tables of all groups.
    """
    raise NotImplementedError


def one_group_table_view(request):
    """
    View with table of one group.
    """
    raise NotImplementedError
