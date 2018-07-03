import django_filters
from django_filters import rest_framework as filters
from .models import InnerStrategy, OuterStrategy, Strategy
from apps.common.filters import IcontainsFilter


class InnerStrategyFilter(filters.FilterSet):
    appId = django_filters.NumberFilter(name='app__id')
    name = IcontainsFilter()

    class Meta:
        model = InnerStrategy
        fields = ('name', 'appId')


class OuterStrategyFilter(filters.FilterSet):
    appId = django_filters.NumberFilter(name='app__id')
    name = IcontainsFilter()

    class Meta:
        model = OuterStrategy
        fields = ('name', 'appId')


class StrategyFilter(filters.FilterSet):
    appId = django_filters.NumberFilter(name='app__id')
    name = IcontainsFilter()

    class Meta:
        model = Strategy
        fields = ('appId', 'name', 'type')
