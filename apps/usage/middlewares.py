from copy import deepcopy
import datetime
import json
from django.conf import settings
from django.http import RawPostDataException
from django.utils.deprecation import MiddlewareMixin
from apps.common.utils import get_response_business_status_code
from apps.task_manager.views import GrayTasksViewSet
from apps.usage.models import Usage
from apps.common.gated_logger import gated_access_logger, gated_debug_logger


class RecordUsageMiddleware(MiddlewareMixin):
    RECORD_VIEW_CLASS = [GrayTasksViewSet]

    @staticmethod
    def _log(request, response):
        try:
            log_dict = {'user': request.user.username, 'resource': request.path, 'method': request.method,
                        'http_status': response.status_code,
                        'response_business_status': get_response_business_status_code(response)}
            log_dict.update(getattr(request, '_usage', {}))
            gated_access_logger.info('{} {}'.format(settings.BACKEND_ACCESS_LOG_PREFIX, json.dumps(log_dict)))
        except TypeError as e:
            raise ValueError(str(e))

    @staticmethod
    def _log_unauthenticated(request, response):
        try:
            if not getattr(response, 'data', None):
                return
            data = deepcopy(response.data)
            if isinstance(data, dict) and isinstance(data.get('data'), dict):
                data['data'].pop('token', None)
            log_dict = {'resource': request.path, 'method': request.method,
                        'http_status': response.status_code,
                        'data': data}
            log_dict.update(getattr(request, '_usage', {}))
            gated_access_logger.info('{} {}'.format(settings.BACKEND_ACCESS_LOG_PREFIX, json.dumps(log_dict)))
        except TypeError as e:
            raise ValueError(str(e))

    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'login' in request.path:
            return
        if request.method == 'GET' and request.GET:
            request._usage = {'params': request.GET.dict()}
        elif request.method == 'POST' and request.POST:
            request._usage = {'params': request.POST.dict()}
        else:
            try:
                if request.body:
                    charset = request.encoding if request.encoding else settings.DEFAULT_CHARSET
                    request._usage = {'params': request.body.decode(encoding=charset)}
            except (ValueError, UnicodeError, RawPostDataException):
                # do nothing, don't break normal work
                pass
            except Exception as e:
                # unexpected exception, log it
                gated_debug_logger.error(str(e))

    def process_response(self, request, response):
        # try to not break the response just because of logging information
        try:
            # record the connection to backend API
            if request.path.startswith('/api') and hasattr(request, 'user'):
                if request.user.is_authenticated():
                    self._log(request, response)
                    request.user.last_connected = datetime.datetime.now()
                    request.user.save()
                    # not arbitrary request or response could satisfy the following requirements
                    if getattr(request.resolver_match.func, 'cls', None) in self.RECORD_VIEW_CLASS and \
                            request.method == 'GET':
                        Usage.objects.create(user=request.user, resource=request.path,
                                             response_http_status=response.status_code,
                                             response_business_status=get_response_business_status_code(response),
                                             method=request.method,
                                             link_from=request.GET.get('from'),
                                             params=getattr(request, '_usage', {}).get('params'))
                else:
                    self._log_unauthenticated(request, response)

        # don't break normal work
        except Exception as e:
            gated_debug_logger.error("RecordUsageMiddleware failed to log: {}".format(str(e)))

        return response
