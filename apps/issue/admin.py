from django.contrib import admin
from . import models
from apps.common.utils import register


class IssueTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class IssueStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class IssueAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status')


class BusinessModuleTreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'level', 'disabled')


admin.site.register(models.Issue, IssueAdmin)
admin.site.register(models.IssueType, IssueTypeAdmin)
admin.site.register(models.IssueStatus, IssueStatusAdmin)
admin.site.register(models.BusinessModuleTree, BusinessModuleTreeAdmin)
register('issue')
