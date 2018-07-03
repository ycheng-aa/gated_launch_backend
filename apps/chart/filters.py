import django_filters
from django_filters import rest_framework as filters
from apps.issue.models import Issue


class UserChartFilter(filters.FilterSet):
    userName = django_filters.CharFilter(name='creator__username')

    class Meta:
        model = Issue
        fields = ('userName',)


class TaskChartFilter(filters.FilterSet):
    appName = django_filters.CharFilter(name='app__name')
    appId = django_filters.NumberFilter(name='app__id')

    class Meta:
        model = Issue
        fields = ('appName', 'appId')
