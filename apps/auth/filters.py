import django_filters
from django_filters import rest_framework as filters
from apps.common.filters import MultiValueFilter
from .models import User
from django.db.models import Q


class UserFilter(filters.FilterSet):
    userName = django_filters.CharFilter(name='username')
    chineseName = django_filters.CharFilter(name='full_name')
    sug = django_filters.CharFilter(method='filter_by_suggestion')
    groupId = MultiValueFilter(name='usergroup__id')

    def filter_by_suggestion(self, qs, name, value):
        return qs.filter(Q(username__icontains=value) | Q(full_name__icontains=value))

    class Meta:
        model = User
        fields = ('id', 'userName', 'chineseName', 'sug', 'phone')
