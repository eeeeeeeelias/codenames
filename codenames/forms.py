"""
Forms for codenames web app:
- AddResultForm
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .consts import AWAY_TEAM_WORDS_NUMBER, HOME_TEAM_WORDS_NUMBER
from .consts import SCORE_CHOICES
from .models import ResultType


class AddResultForm(forms.Form):
    """
    Form to add result of one game.
    """
    def __init__(self, *args, **kwargs):
        if "games_choices" in kwargs:
            games_choices = kwargs.pop("games_choices")

        super().__init__(*args, **kwargs)

        self.fields["game"] = forms.CharField(
            label=_("Choose a game:"),
            widget=forms.Select(choices=games_choices)
        )

        # GameResult field must be first
        self.order_fields(["game"])

    result_type = forms.ModelChoiceField(
        label=_("Choose result type:"),
        queryset=ResultType.objects.all(),
        widget=forms.Select(
            attrs={"onchange": "updateScoreFieldState();"}
        )
    )

    score = forms.CharField(
        label=_("Choose score:"),
        widget=forms.Select(choices=[sc for sc in SCORE_CHOICES if sc[0] >= 0]),
        initial=0
    )

    home_team_fouls = forms.IntegerField(
        label=_("Team 1 fouls:"),
        min_value=0,
        max_value=AWAY_TEAM_WORDS_NUMBER,
        initial=0
    )
    away_team_fouls = forms.IntegerField(
        label=_("Team 2 fouls:"),
        min_value=0,
        max_value=HOME_TEAM_WORDS_NUMBER,
        initial=0
    )

    def clean_score(self):
        score = int(self.cleaned_data["score"])
        result_type = self.cleaned_data["result_type"]
        if not result_type.is_home_win:
            score *= -1
        if result_type.is_auto:
            if score != 0:
                self.add_error(
                    "score",
                    ValidationError(
                        _("Do not choose score if game didn't end normally"),
                        code="score not neede")
                )
        else:
            if score == 0:
                self.add_error(
                    "score",
                    ValidationError(_("Please choose score"),
                                    code="score not chosen")
                )
        return score
