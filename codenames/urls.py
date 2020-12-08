"""
Urls for codenames app.
"""

from django.urls import path, re_path
from . import views

app_name = "codenames"

urlpatterns = [
    re_path(r"^(?P<group_name>[A-Za-z])/$", views.one_group_table_view, name="one_group_table"),
    path("", views.start_view, name="index"),
    path("results/", views.all_groups_tables_view, name="all_groups_tables"),
    path("<str:group_name>/results/",
         views.one_group_table_view,
         name="one_group_table"),
    path("cup<int:cup_number>/results/",
         views.all_groups_tables_view,
         name="all_groups_tables_of_cup"),
    path("cup<int:cup_number>/results/<str:group_name>",
         views.one_group_table_view,
         name="one_group_table_of_cup"),
    path("<str:group_name>/add_result/", views.add_result,
         name="add_result"),
]
