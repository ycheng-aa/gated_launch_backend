import django_filters
from django_filters import rest_framework as filters
from .models import GrayTask, IssueExtField
from apps.common.filters import IcontainsFilter, ExtBooleanFilter


class GrayTaskFilter(filters.FilterSet):
    appId = django_filters.CharFilter(name='app__id')
    statusId = django_filters.CharFilter(name='current_status__id')
    isDisplay = django_filters.CharFilter(name='is_display', method='filter_display')
    name = IcontainsFilter(name="task_name")
    isJoinKesutong = ExtBooleanFilter(name="is_join_kesutong")

    class Meta:
        model = GrayTask
        fields = ('id', 'appId', 'statusId', 'isDisplay', 'isJoinKesutong')

    def filter_display(self, queryset, name, value):
        # app置顶任务，查询时此参数 必须为true
        if str(value).lower() == 'true':
            return queryset.filter(is_display=True)
        return queryset


class IssueExtFieldFilter(filters.FilterSet):
    isOptional = django_filters.BooleanFilter(name='is_optional')

    class Meta:
        model = IssueExtField
        fields = ('name', 'default', 'isOptional', 'type')
