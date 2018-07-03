from django.contrib import admin
from . import models


class AwardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'desc')


class Awardee(admin.ModelAdmin):
    list_display = ('id', 'award', 'user', 'desc')


admin.site.register(models.Award, AwardAdmin)
admin.site.register(models.Awardee, Awardee)
