from django.contrib import admin

from bot.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Chat)
admin.site.register(ChatMember)
admin.site.register(ChatSettings)
admin.site.register(AccessSettings)
admin.site.register(AccessSettingsObject)

