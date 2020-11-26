"""
Models for codenamess app.
"""

import typing as tp

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

from .consts import CURRENT_CUP_NUMBER
from .consts import GROUP_NAMES, MAX_GROUP_SIZE
from .consts import EARLY_FEE_SIZE, LATE_FEE_SIZE
from .consts import SCORE_CHOICES
from .consts import MAX_ARENAS_NUMBER
from .consts import get_non_auto_score_string


class Cup(models.Model):
    """
    Fields:
    number
    [date]
    [place]
    """
    number = models.IntegerField(
        default=CURRENT_CUP_NUMBER,
        choices=[(i, i) for i in range(1, CURRENT_CUP_NUMBER + 1)]
    )

    date = models.DateField(null=True)
    place = models.CharField(null=True, max_length=30)

    def __str__(self):
        return f'Cup {self.number}'


def get_current_cup_id():
    return Cup.objects.get(number=CURRENT_CUP_NUMBER).id


class Group(models.Model):
    """
    Fields:
    ->cup
    name
    """

    cup = models.ForeignKey(
        Cup,
        default=get_current_cup_id,
        on_delete=models.CASCADE,
        related_name="%(class)scup"
    )

    name = models.CharField(
        default=GROUP_NAMES[0],
        max_length=1,
        choices=GROUP_NAMES
    )

    @property
    def short(self):
        return f"{self.name}"

    @property
    def long(self):
        return f"{self.cup}, group {self.name}"

    def __str__(self):
        return self.long


def get_empty_group_id():
    return Group.objects.get(name="Z")


class Player(models.Model):
    """
    Fields:
    first_name
    last_name
    """

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    @property
    def short(self):
        return (
            f'{self.last_name.capitalize()}'
            f' '
            f'{self.first_name[0].capitalize()}'
            f'.'
        )

    @property
    def long(self):
        return f'{self.last_name.capitalize()} {self.first_name.capitalize()}'

    def __str__(self):
        return self.long


def get_empty_player_id():
    return Player.objects.get_or_create(first_name="$Name",
                                        last_name="$No")[0].id


def get_another_empty_player_id():
    return Player.objects.get_or_create(first_name="$Suchplayer",
                                        last_name="$No")[0].id


class Team(models.Model):
    """
    Fields:
    ->first_player
    [->second_player]
    [->group]
    ->cup
    is_paid
    [has_come]
    [seed]
    """

    first_player = models.ForeignKey(
        Player,
        default=get_empty_player_id,
        on_delete=models.CASCADE,
        related_name="first_player"
    )
    second_player = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="second_player"
    )

    group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="%(class)sgroup"
    )
    cup = models.ForeignKey(
        Cup,
        default=get_current_cup_id,
        on_delete=models.CASCADE,
        related_name="%(class)scup"
    )

    is_paid = models.BooleanField(
        default=False
    )

    has_come = models.BooleanField(
        default=False,
        null=True,
        blank=True
    )

    seed = models.IntegerField(
        null=True,
        blank=True,
        choices=[(seed, seed) for seed in range(0, MAX_GROUP_SIZE)]
    )

    fee_size = models.IntegerField(
        default=EARLY_FEE_SIZE,
        choices=[(EARLY_FEE_SIZE, EARLY_FEE_SIZE),
                 (LATE_FEE_SIZE, LATE_FEE_SIZE)]
    )

    @property
    def short(self):
        return f"{self.first_player.short}/{self.second_player.short}"

    @property
    def long(self):
        return f"{self.first_player.long}/{self.second_player.long}"

    def __str__(self):
        return self.long


def get_empty_team_id():
    return Team.objects.get_or_create(
        first_player=get_empty_player_id(),
        second_player=get_another_empty_player_id()
    ).id


class ResultType(models.Model):
    """
    Fields:
    abbr
    _description
    is_auto
    is_home_win
    [_auto_score]
    """

    abbr = models.CharField(max_length=2)
    _description = models.CharField(max_length=30)
    is_auto = models.BooleanField(default=False)
    is_home_win = models.BooleanField(default=True)
    _auto_score = models.IntegerField(
        null=True,
        blank=True,
        choices=SCORE_CHOICES,
    )

    @property
    def description(self):
        return self._description

    @property
    def is_away_win(self):
        return not self.is_home_win

    @property
    def home_auto_score(self):
        if self.is_home_win:
            return 0
        return -self._auto_score

    @property
    def away_auto_score(self):
        if self.is_away_win:
            return 0
        return self._auto_score

    def __str__(self):
        return self.description

    def clean(self):
        if self.is_auto and self._auto_score is None:
            raise ValidationError(_('specify auto score for auto end game'))
        if not self.is_auto and self._auto_score is not None:
            raise ValidationError(
                _('you cannot specify auto score for non-auto end game'))
        if self.is_auto:
            if self.is_home_win and self._auto_score < 0:
                raise ValidationError(
                    _('home team auto win: chosen score says the opposite'))
            if self.is_away_win and self._auto_score > 0:
                raise ValidationError(
                    _('away team auto win: chosen score says the opposite'))


class Arena(models.Model):
    """
    Fields:
    ->group
    number
    [room]
    """

    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="%(class)sgroup"
    )

    number = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_ARENAS_NUMBER)]
    )

    room = models.CharField(blank=True, null=True, max_length=30)

    @property
    def short(self):
        return f"{self.group.short}{self.number}"

    @property
    def long(self):
        return f"({self.group.cup}) {self.group.short}{self.number}"

    def __str__(self):
        return self.long


def get_empty_arena_id():
    return Arena.objects.get_or_create(number=0).id


class GameResult(models.Model):
    """
    Fields:
    ->group
    ->home_team
    ->away_team
    ->arena
    [->result_type]
    round_number
    score
    """

    group = models.ForeignKey(
        Group,
        default=get_empty_group_id,
        on_delete=models.CASCADE,
        related_name="%(class)sgroup"
    )

    home_team = models.ForeignKey(
        Team,
        default=get_empty_team_id,
        on_delete=models.CASCADE,
        related_name="home_team"
    )
    away_team = models.ForeignKey(
        Team,
        default=get_empty_team_id,
        on_delete=models.CASCADE,
        related_name="away_team"
    )

    arena = models.ForeignKey(
        Arena,
        default=get_empty_arena_id,
        on_delete=models.CASCADE,
        related_name="arena",
    )

    result_type = models.ForeignKey(
        ResultType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="result_type"
    )

    round_number = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(MAX_GROUP_SIZE - 1)]
    )

    # 4 == home team 4:0 away_team
    # -7 == home_team 0:7 away_team
    # 0 == auto result_type
    score = models.IntegerField(
        default=0,
        choices=SCORE_CHOICES
    )

    @property
    def is_finished(self) -> bool:
        return self.result_type is not None

    @property
    def home_score(self) -> tp.Optional[str]:
        if not self.is_finished:
            return None
        return get_non_auto_score_string(self.score)

    @property
    def away_score(self) -> tp.Optional[str]:
        if not self.is_finished:
            return None
        return get_non_auto_score_string(-self.score)

    def clean(self):
        if self.result_type.is_auto and self.score != 0:
            raise ValidationError(_('do not choose score for auto end game'))
        if not self.result_type.is_auto and self.score == 0:
            raise ValidationError(_('choose score for non-auto end game'))
        if self.result_type.is_home_win and self.score < 0:
            raise ValidationError(
                _('home team won: chosen score says the opposite'))
        if self.result_type.is_away_win and self.score > 0:
            raise ValidationError(
                _('away team won: chosen score says the opposite'))
