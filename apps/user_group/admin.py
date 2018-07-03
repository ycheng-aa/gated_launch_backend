from django.contrib import admin
from . import models
from apps.common.utils import register


class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'app')


admin.site.register(models.UserGroup, UserGroupAdmin)
register('user_group')
