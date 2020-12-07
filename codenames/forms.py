from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .consts import AWAY_TEAM_WORDS_NUMBER, HOME_TEAM_WORDS_NUMBER
from .consts import SCORE_CHOICES
from .models import ResultType


class AddResultForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if "games_choices" in kwargs:
            games_choices = kwargs.pop("games_choices")

        super().__init__(*args, **kwargs)

        self.fields["game"] = forms.CharField(
            label=_("Choose a game"),
            widget=forms.Select(choices=games_choices)
        )

        # GameResult field must be first
        self.order_fields(["game"])

    result_type = forms.ModelChoiceField(
        label=_("Choose result type"),
        queryset=ResultType.objects.all(),
        widget=forms.Select(
            attrs={"onchange": "updateScoreFieldState();"}
        )
    )

    score = forms.CharField(
        label=_("Choose score"),
        widget=forms.Select(choices=SCORE_CHOICES),
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

    def clean(self):
        cleaned_data = super().clean()
        result_type = cleaned_data.get("result_type")
        score = int(cleaned_data.get("score"))

        if result_type.is_auto:
            # If team autowins, score is chosen automatically
            if score != 0:
                self.add_error(
                    "score",
                    ValidationError(
                        _("Do not choose score if game didn't end normally"),
                        code="score not neede")
                )
        else:
            # If team covers all its words, you need to choose score
            if score == 0:
                self.add_error(
                    "score",
                    ValidationError(_("Please choose score"),
                                    code="score not chosen")
                )
            if result_type.abbr == "W1" and score < 0:
                self.add_error(
                    "score",
                    ValidationError(_("Choose correct score for team 1 win"),
                                    code="negative score for home win")
                )
            if result_type.abbr == "W2" and score > 0:
                self.add_error(
                    "score",
                    ValidationError(_("Choose correct score for team 2 win"),
                                    code="positive score for home win")
                )
