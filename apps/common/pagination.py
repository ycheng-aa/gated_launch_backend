import sys
from collections import OrderedDict

from django.conf import settings

from rest_framework import pagination
from rest_framework.response import Response


class GatedLaunchPagination(pagination.PageNumberPagination):
    page_size = getattr(settings, 'REST_API_PAGE_SIZE', sys.maxsize)
    page_size_query_param = getattr(settings,
                                    'REST_API_PAGE_SIZE_QUERY_PARAM',
                                    'pageSize')
    max_page_size = getattr(settings,
                            'REST_API_MAX_PAGE_SIZE',
                            100)

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                if int(request.query_params[self.page_size_query_param]) <= 0:
                    return sys.maxsize
                else:
                    return pagination._positive_int(
                        request.query_params[self.page_size_query_param],
                        strict=True,
                        cutoff=self.max_page_size
                    )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('total', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
