"""
Views for codenames app.
"""

import typing as tp

from django.http import Http404
from django.shortcuts import render
from django.template.defaulttags import register
from django.utils.translation import gettext_lazy as _

from .consts import CURRENT_CUP_NUMBER
from .forms import AddResultForm
from .models import Cup, GameResult, Group, ResultType
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

    group_headers = {gn: render_result_table_header(cup_groups.get(name=gn))
                     for gn in group_names}
    group_tables = {gn: render_result_table_content(cup_groups.get(name=gn))
                    for gn in group_names}

    upcoming_games_lists = {
        gn: get_upcoming_games_schedule(cup_groups.get(name=gn))
        for gn in group_names
    }
    recent_games_lists = {
        gn: get_recent_games_schedule(cup_groups.get(name=gn))
        for gn in group_names
    }

    context = {
        "cup_number": cup.number,
        "group_names": group_names,
        "groups_headers": group_headers,
        "groups_tables": group_tables,
        "upcoming_games": upcoming_games_lists,
        "recent_games": recent_games_lists,
    }
    return render(request, "codenames/all_groups_tables.html", context)


def one_group_table_view(request, group_name, *,
                         cup_number=CURRENT_CUP_NUMBER):
    """
    View with table of one group.
    """
    group_name = group_name.upper()
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

    upcoming_games_list = get_upcoming_games_schedule(group)
    recent_games_list = get_recent_games_schedule(group)

    context = {
        "cup_number": cup_number,
        "group_name": group.name,
        "group_header": group_header,
        "group_table": group_table,
        "upcoming_games": upcoming_games_list,
        "recent_games": recent_games_list,
    }
    return render(request, "codenames/one_group_table.html", context)


def get_games_choices(group_name: str):
    games_list = sorted(
        GameResult.objects.filter(group__name=group_name),
        key=lambda x: (x.is_finished, x.round_number))
    return [
        (game.id, game) for game in games_list
    ]



def add_result(request, group_name: str):
    last_add_result: tp.Optional[str] = None
    if request.method == "POST":
        form = AddResultForm(request.POST,
                             games_choices=get_games_choices(group_name))
        if form.is_valid():
            data = request.POST
            result_type = ResultType.objects.get(id=data["result_type"])
            score = int(data["score"])
            if result_type.is_away_win:
                score *= -1
            GameResult.objects.filter(id=int(data["game"])).update(
                result_type=data["result_type"],
                score=score,
                home_team_fouls=data["home_team_fouls"],
                away_team_fouls=data["away_team_fouls"],
            )
            last_add_result = _("Result added successfully!")
            form = AddResultForm(games_choices=get_games_choices(group_name))
        else:
            last_add_result = _("Failed to add result!")
    elif request.method == "GET" or form.is_valid():
        form = AddResultForm(games_choices=get_games_choices(group_name))

    auto_result_ids: tp.List[int] = [
        rt.id for rt in ResultType.objects.all() if rt.is_auto
    ]
    context = {
        "group_name": group_name,
        "last_add_result": last_add_result,
        "form": form,
        "auto_result_ids": auto_result_ids,
    }
    return render(request, "codenames/add_result.html", context)
