"""
Some data to render result tables and to break ties.
"""

# Order of columns in result table
TABLE_COLUMNS_BEFORE_RESULTS_ORDER = [
    "place",
    "team",
]
TABLE_COLUMNS_AFTER_RESULTS_ORDER = [
    "played",
    "won",
    "lost",
    "words_difference",
    "fouls",
]

# Order and weight of tie breakers in group
# Start tie breaker name with "optional"
# if tie breaker is used only when all tied teams
# finished all games with each other
TIE_BREAKERS_ORDER = [
    "won",
    "optional_won_between",
    "absences",
    "serious_fouls",
    "fouls",
    "black_loses",
    "optional_black_loses_between",
    "words_difference",
    "optional_words_difference_between",
    "games_played",
    "seed"
]
TIE_BREAKERS_WEIGHTS = {
    "won": +1,
    "optional_won_between": +1,
    "absences": -1,
    "serious_fouls": -1,
    "fouls": -1,
    "black_loses": -1,
    "optional_black_loses_between": -1,
    "words_difference": +1,
    "optional_words_difference_between": +1,
    "games_played": +1,
    "seed": -1,
}

OPTIONAL_TIE_BREAKERS = {
    "optional_won_between",
    "optional_black_loses_between",
    "optional_words_difference_between",
}
