from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView
from apps.auth.models import Role
from apps.common.models import AppModule


# 接口文档:
# http://wiki.ffan.biz/pages/viewpage.action?pageId=18514633#CommonApp接口文档-获取客户端问题模块列表
# http://wiki.ffan.biz/pages/viewpage.action?pageId=18514633#CommonApp接口文档-新增客户端问题模块列表
# http://wiki.ffan.biz/pages/viewpage.action?pageId=18514633#CommonApp接口文档-修改客户端问题模块列表
# http://wiki.ffan.biz/pages/viewpage.action?pageId=18514633#CommonApp接口文档-删除客户端问题模块列表


class AppModuleView(BenchmarkAPIView):
    '''
    客户端问题模块
    '''
    primary_model = AppModule
    access = {
        'get': 'user', 'post': Role.APP_OWNER, 'put': Role.APP_OWNER, 'delete': Role.APP_OWNER
    }
