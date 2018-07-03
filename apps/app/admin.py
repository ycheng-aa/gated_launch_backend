from django.contrib import admin
from . import models


class AppAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class AppTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


class AppComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'operator')


admin.site.register(models.App, AppAdmin)
admin.site.register(models.AppType, AppTypeAdmin)
admin.site.register(models.AppComponent, AppComponentAdmin)
