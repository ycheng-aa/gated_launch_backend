from django.contrib import admin
from . import models
from apps.common.utils import register


class GrayStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class GrayTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_name', 'app')


admin.site.register(models.GrayStatus, GrayStatusAdmin)
admin.site.register(models.GrayTask, GrayTaskAdmin)

register('task_manager')
