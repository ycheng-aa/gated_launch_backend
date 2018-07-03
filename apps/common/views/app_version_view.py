from apps.common.utils import get_app_versions
from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView


# 接口文档:
# http://wiki.ffan.biz/pages/viewpage.action?pageId=18514633#CommonApp接口文档-获取版本列表


class AppVersionView(BenchmarkAPIView):
    '''
    获取内灰版本列表
    '''
    access = {'get': 'user', 'post': None, 'put': None, 'delete': None}
    apphub_android = 0
    apphub_ios = 1

    def get_model(self):
        self.params.update(self.uri_params)
        app_id = self.params.get('app', None)
        app_type = self.params.get('app_type', None)
        return get_app_versions(app_id, app_type)
