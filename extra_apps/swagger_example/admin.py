from django.contrib import admin
from . import models


class SwaggerExampleUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')


admin.site.register(models.ExampleUser, SwaggerExampleUserAdmin)
