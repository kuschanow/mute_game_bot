from django.contrib import admin

from games.models import *

# Register your models here.
admin.site.register(Punishment)
admin.site.register(RandomChoiceGame)
admin.site.register(RandomChoiceGamePlayer)
admin.site.register(RandomChoiceGameResult)
admin.site.register(RandomChoiceGameLoser)
