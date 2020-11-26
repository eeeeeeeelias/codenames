BLACK_AUTO_SCORE: int = 4
TIME_AUTO_SCORE: int = 4
SERIOUS_FOUL_AUTO_SCORE: int = 8
ABSENCE_AUTO_SCORE: int = 8


class ConstResultType:
    def __init__(self,
                 id_: str,
                 /,
                 *,
                 description: str = None,
                 is_auto: bool = None,
                 is_home_win: bool = None,
                 auto_score: int = None):
        if description is None:
            raise TypeError(_('missing description'))
        if is_auto is None:
            raise TypeError(_('missing is_auto'))
        if is_home_win is None:
            raise TypeError(_('missing is_home_win'))
        self._id = id_
        self._description = description
        self._is_auto = is_auto
        self._is_home_win = is_home_win
        if is_auto and auto_score is None:
            raise TypeError(_('specify auto score for auto end game'))
        if not is_auto and auto_score is not None:
            raise TypeError(_('you cannot specify auto score for non-auto end game'))
        self._auto_score = auto_score

    @property
    def description(self):
        return self._description

    @property
    def is_auto(self):
        return self._is_auto

    @property
    def is_home_win(self):
        return self._is_home_win

    @property
    def is_away_win(self):
        return not self._is_home_win

    @property
    def home_auto_score(self):
        if self._is_home_win:
            return 0
        else:
            return -self._auto_score

    @property
    def away_auto_score(self):
        if self._is_home_win:
            return self._auto_score
        else:
            return 0

    @property
    def auto_score(self):
        return self._auto_score

    @property
    def id(self):
        return self._id

    @property
    def for_select(self):
        return self._id, self._description


RESULT_TYPES = {
    'W1': ConstResultType('W1', description='Team 1 covered all words', is_auto=False, is_home_win=True),
    'W2': ConstResultType('W2', description='Team 2 covered all words', is_auto=False, is_home_win=False),
    'B2': ConstResultType('B2', description='Team 1 black lose', is_auto=True, is_home_win=False, auto_score=-BLACK_AUTO_SCORE),
    'B1': ConstResultType('B1', description='Team 2 black lose', is_auto=True, is_home_win=True, auto_score=BLACK_AUTO_SCORE),
    'T2': ConstResultType('T2', description='Team 1 time lose', is_auto=True, is_home_win=False, auto_score=-TIME_AUTO_SCORE),
    'T1': ConstResultType('T1', description='Team 2 time lose', is_auto=True, is_home_win=True, auto_score=TIME_AUTO_SCORE),
    'A2': ConstResultType('A2', description='Team 1 absence', is_auto=True, is_home_win=False, auto_score=-ABSENCE_AUTO_SCORE),
    'A1': ConstResultType('A1', description='Team 2 absence', is_auto=True, is_home_win=True, auto_score=ABSENCE_AUTO_SCORE),
    'F2': ConstResultType('F2', description='Team 1 serious foul', is_auto=True, is_home_win=False, auto_score=-SERIOUS_FOUL_AUTO_SCORE),
    'F1': ConstResultType('F1', description='Team 2 serious foul', is_auto=True, is_home_win=True, auto_score=SERIOUS_FOUL_AUTO_SCORE),
}
