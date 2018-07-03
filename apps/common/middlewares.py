import collections
import copy
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status


class ResponseFormatMiddleware(MiddlewareMixin):
    # may by should notify permission and unauthorized problem
    # code to client
    ALLOWED_CLIENT_ERROR_CODES = (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    @staticmethod
    def _get_http_status_code(code):
        result = code
        if status.is_success(code) or status.is_client_error(code):
            result = status.HTTP_200_OK
        elif status.is_server_error(code):
            result = status.HTTP_500_INTERNAL_SERVER_ERROR
        return result

    @classmethod
    def _get_to_business_status_code(cls, code):
        result = code
        if status.is_success(code):
            result = status.HTTP_200_OK
        elif status.is_client_error(code) and code not in cls.ALLOWED_CLIENT_ERROR_CODES:
            result = status.HTTP_400_BAD_REQUEST
        return result

    @classmethod
    def _convert_data(cls, response, business_code):
        converted_data = collections.OrderedDict()
        converted_data['status'] = business_code
        if business_code == status.HTTP_200_OK:
            converted_data['msg'] = "成功"
            if response.data:
                # msg in data should be displayed anyway
                if response.data.get('msg'):
                    converted_data['msg'] = response.data.pop('msg')
                converted_data['data'] = response.data
        else:
            # error happens, move the message to 'msg' part
            # assume at most one type of following message appears
            ori_data = copy.deepcopy(response.data)
            for key in ('msg', 'message', 'detail', 'non_field_errors'):
                if key in response.data:
                    msg = response.data.pop(key)
                    if isinstance(msg, list) and len(msg) == 1:
                        msg = msg[0]
                    converted_data['msg'] = msg
            # still have other messages, unpredictable content
            if response.data:
                converted_data['msg'] = ori_data

        response.data = converted_data
        response.content = response.rendered_content

    def process_response(self, request, response):
        if (response.get('content-type') == 'application/json' and isinstance(response.data, dict)) or\
                response.status_code == status.HTTP_204_NO_CONTENT:
            status_code = self._get_http_status_code(response.status_code)
            business_code = self._get_to_business_status_code(response.status_code)
            self._convert_data(response, business_code)
            response.status_code = status_code
        return response

    @staticmethod
    def process_request(request):
        setattr(request, '_dont_enforce_csrf_checks', True)
