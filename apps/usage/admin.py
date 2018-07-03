from django.contrib import admin
from . import models
from apps.common.utils import register


class UsageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'resource', 'method', 'link_from', 'created_time')


class PropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'key', 'value')


class EventTrackingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type')


admin.site.register(models.Usage, UsageAdmin)
admin.site.register(models.Property, PropertyAdmin)
admin.site.register(models.EventTracking, EventTrackingAdmin)
register('usage')
