from django.contrib import admin
from .models import Competition, Match, Prediction, CompetitionResult

admin.site.register(Competition)
admin.site.register(Match)
admin.site.register(Prediction)
admin.site.register(CompetitionResult)
