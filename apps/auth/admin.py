from django.contrib import admin
from . import models


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')


class DepAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Department, DepAdmin)
