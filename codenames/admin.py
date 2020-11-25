from django.contrib import admin
from .models import Arena, Cup, GameResult, Group, Player, ResultType, Team

admin.site.register(Cup)
admin.site.register(Group)
admin.site.register(Player)
admin.site.register(Team)
admin.site.register(ResultType)
admin.site.register(Arena)
admin.site.register(GameResult)
