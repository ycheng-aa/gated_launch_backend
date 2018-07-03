import copy
import operator
import datetime
from functools import reduce
from django.db.models import Q, Count
import django_filters
from django_filters import rest_framework as filters
from rest_framework.settings import api_settings
import six
from apps.auth.models import Department
from apps.common.filters import MultiValueFilter, IcontainsFilter
from .models import Issue, IssueStatus


class IssueFilter(filters.FilterSet):
    appId = django_filters.CharFilter(name='app__id')
    taskId = django_filters.CharFilter(name='task__id')
    statusId = django_filters.CharFilter(name='status__id')
    creator = IcontainsFilter(name='creator__username')
    statusName = django_filters.CharFilter(name='status__name')
    reportSource = django_filters.CharFilter(name='report_source__name')
    jiraId = django_filters.CharFilter(name='jira_link')
    priority = django_filters.CharFilter(name='priority__desc')
    score = MultiValueFilter(name='score')
    createdTime = django_filters.CharFilter(method='filter_by_created_time')
    department = django_filters.CharFilter(method='filter_by_dep')
    statusNameOrder = django_filters.CharFilter(method='order_by_status_name')
    updatedAfter = django_filters.DateTimeFilter(name='updated_time', lookup_expr='gt')
    startDate = django_filters.DateFilter(name='created_time', lookup_expr='gte')
    endDate = django_filters.DateFilter(method='filter_by_end_date')
    operator = django_filters.CharFilter(name='operator__username')

    class Meta:
        model = Issue
        fields = ('title', 'appId', 'taskId', 'statusId', 'creator', 'statusName', 'reportSource', 'jiraId', 'priority',
                  'score', 'createdTime', 'operator')

    def filter_by_dep(self, qs, name, value):
        query_set = Department.objects.filter(name__startswith=value)
        dep_id_array = [dep.id for dep in Department.objects.get_queryset_descendants(query_set, include_self=True)]
        return qs.filter(creator__department__in=dep_id_array)

    def order_by_status_name(self, qs, name, value):
        order_list = value.split(',')
        status_name_id_dict = dict((status.name, status.id) for status in IssueStatus.objects.all())

        # must all values are legal to prevent SQL injection
        if set(order_list) - set(status_name_id_dict.keys()):
            return qs

        status_id_order = [status_name_id_dict[name] for name in order_list]
        status_column = "{}.{}".format(Issue._meta.db_table, Issue._meta.get_field('status').column)
        created_time_column = "{}.{}".format(Issue._meta.db_table, Issue._meta.get_field('created_time').column)
        case_sql = '(CASE '
        value = 1
        for status_id in status_id_order:
            case_sql += """ WHEN {}={} then {} """.format(status_column, status_id, value)
            value += 1
        case_sql += " end) "

        return qs.extra(select={'status_order': case_sql}, order_by=['status_order', created_time_column])

    def filter_by_created_time(self, qs, created_time, value):
        return qs.filter(created_time__startswith=value)

    def filter_by_end_date(self, qs, created_time, value):
        end_time = (value + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        return qs.filter(created_time__lte=end_time)

    def filter_by_extended_fields(self, qs, query_params):
        if not query_params:
            return qs
        q_list = []
        for name, value in query_params.items():
            q_list.append(Q(ext_values__field__name=name, ext_values__value=value))
        qs = qs.filter(reduce(operator.or_, q_list)).distinct().\
            annotate(field_count=Count('ext_values')).filter(field_count=len(query_params))
        return qs

    @property
    def qs(self):
        qs = super().qs
        query_params = copy.deepcopy(self.request.query_params)
        for name, _ in six.iteritems(self.filters):
            query_params.pop(name, None)
        for name in (api_settings.DEFAULT_PAGINATION_CLASS.page_size_query_param, 'page'):
            query_params.pop(name, None)
        qs = self.filter_by_extended_fields(qs, query_params)
        return qs
