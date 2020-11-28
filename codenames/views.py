"""
Views for codenames app.
"""

import typing as tp

from django.http import Http404
from django.shortcuts import render
from django.template.defaulttags import register
from django.utils.translation import gettext_lazy as _

from .consts import CURRENT_CUP_NUMBER
from .models import Cup, Group
from .table_render import render_result_table_content
from .table_render import render_result_table_header
from .table_render import get_recent_games_schedule, get_upcoming_games_schedule


NON_EXISTING_CUP_ERROR_MESSAGE = _("There is no such cup")
NON_EXISTING_GROUP_ERROR_MESSAGE = _("There is no such group")


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def start_view(request):
    """
    Start view of tounament website.
    """
    groups = [
        g.name for g in Group.objects.filter(cup__number=CURRENT_CUP_NUMBER,
                                             dummy=False)
    ]
    context = {
        "group_names": groups
    }
    return render(request, "codenames/start_page.html", context)


def all_groups_tables_view(request, *, cup_number=CURRENT_CUP_NUMBER):
    """
    View with tables of all groups.
    """
    try:
        cup = Cup.objects.get(number=cup_number)
    except Cup.DoesNotExist as cup_no_exist:
        raise Http404(NON_EXISTING_CUP_ERROR_MESSAGE) from cup_no_exist
    cup_groups = Group.objects.filter(cup__number=cup_number, dummy=False)
    group_names: tp.List[str] = sorted(cg.name for cg in cup_groups)
    print(group_names)
    group_headers = {gn: render_result_table_header(cup_groups.get(name=gn))
                     for gn in group_names}
    group_tables = {gn: render_result_table_content(cup_groups.get(name=gn))
                    for gn in group_names}

    context = {
        "cup_number": cup.number,
        "group_names": group_names,
        "groups_headers": group_headers,
        "groups_tables": group_tables,
    }
    return render(request, "codenames/all_groups_tables.html", context)


def one_group_table_view(request, group_name, *,
                         cup_number=CURRENT_CUP_NUMBER):
    """
    View with table of one group.
    """
    try:
        Cup.objects.get(number=cup_number)
    except Cup.DoesNotExist as cup_no_exist:
        raise Http404(NON_EXISTING_CUP_ERROR_MESSAGE) from cup_no_exist
    try:
        group = Group.objects.get(name=group_name, cup__number=cup_number)
    except Group.DoesNotExist as group_no_exist:
        raise Http404(NON_EXISTING_GROUP_ERROR_MESSAGE) from group_no_exist

    group_header = render_result_table_header(group)
    group_table = render_result_table_content(group)

    upcoming_games = get_upcoming_games_schedule(group)
    recent_games = get_recent_games_schedule(group)

    context = {
        "cup_number": cup_number,
        "group_name": group.name,
        "group_header": group_header,
        "group_table": group_table,
        "upcoming_games": upcoming_games,
        "recent_games": recent_games,
    }
    return render(request, "codenames/one_group_table.html", context)
