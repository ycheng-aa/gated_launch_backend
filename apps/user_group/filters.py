import django_filters
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from apps.auth.models import Department
from apps.common.filters import IcontainsFilter
from .models import UserGroup


class UserGroupFilter(filters.FilterSet):
    appName = django_filters.CharFilter(name='app__name')
    appId = django_filters.Filter(name='app')
    type = django_filters.CharFilter(name='type__name')
    name = IcontainsFilter()

    class Meta:
        model = UserGroup
        fields = ('name', 'appName', 'appId', 'type')


class UserGroupMemberFilter(filters.FilterSet):
    account = IcontainsFilter(name='username')

    # 一级部门领导直接部门就是一级部门
    departmentLevel2 = django_filters.CharFilter(method='filter_by_l2_dep')
    departmentLevel1 = django_filters.CharFilter(method='filter_by_l1_dep')

    def filter_by_l2_dep(self, qs, name, value):
        return self._filter_by_dep_with_level(qs, value, 1)

    def filter_by_l1_dep(self, qs, name, value):
        return self._filter_by_dep_with_level(qs, value, 0)

    @staticmethod
    def _filter_by_dep_with_level(qs, value, level):
        query_set = Department.objects.filter(name=value, level=level)
        dep_id_array = [dep.id for dep in Department.objects.get_queryset_descendants(query_set, include_self=True)]
        return qs.filter(department__in=dep_id_array)

    class Meta:
        model = get_user_model()
        fields = ('account', 'departmentLevel1', 'departmentLevel2', 'phone')


class DepartmentFilter(filters.FilterSet):
    parent = django_filters.CharFilter(name='parent__name')

    class Meta:
        model = Department
        fields = ('name', 'parent', 'level')
