from django.contrib import admin
from . import models


# Register your models here.
class ImageAdmin(admin.ModelAdmin):
    list_display = ('image_name', 'image_id')


class PropertyAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')


admin.site.register(models.Image, ImageAdmin)
admin.site.register(models.Property, PropertyAdmin)
