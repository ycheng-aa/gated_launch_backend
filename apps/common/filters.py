import functools
from django.forms import SelectMultiple
from django_filters import Filter, CharFilter


def value_is_not_empty(func):
    @functools.wraps(func)
    def _decorator(self, qs, value):
        if not value:
            return qs
        else:
            if value == ['']:
                value = []
            return func(self, qs, value)

    return _decorator


class MultiValueFilter(Filter):

    def __init__(self, name=None, distinct=True):
        super().__init__(widget=SelectMultiple, name=name, distinct=distinct)

    @value_is_not_empty
    def filter(self, qs, value):
        qs = qs.filter(**{self.name + '__in': value})
        if self.distinct:
            qs = qs.distinct()
        return qs


class IcontainsFilter(CharFilter):

    def filter(self, qs, value):
        if value:
            return qs.filter(**{self.name + '__icontains': value})
        return qs


class ExtBooleanFilter(CharFilter):

    def filter(self, qs, value):
        true_values = {
            't', 'T',
            'y', 'Y', 'yes', 'YES',
            'true', 'True', 'TRUE',
            'on', 'On', 'ON',
            '1', 1,
            True
        }
        false_values = {
            'f', 'F',
            'n', 'N', 'no', 'NO',
            'false', 'False', 'FALSE',
            'off', 'Off', 'OFF',
            '0', 0, 0.0,
            False
        }
        if value in true_values:
            value = True
        elif value in false_values:
            value = False
        else:
            return qs
        return qs.filter(**{self.name: value})
