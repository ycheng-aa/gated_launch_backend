from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from apps.task_manager.models import GrayTask
from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView
from .models import App
from apps.auth.models import Role
from apps.auth.models import UserGroupType
from apps.utils.utils import owner_app_id, get_task_detail_page_path, get_task_file_issue_page_path


class AppView(BenchmarkAPIView):
    '''
    客户端管理APP 接口
    '''
    access = {
        'get': 'user',
        'post': (Role.ADMIN,),
        'put': (Role.APP_OWNER, Role.ADMIN),
        'delete': (Role.ADMIN,)
    }

    primary_model = App

    def get_model(self):
        if "_user" in self.params:
            # 任意权限用户都可通过该参数的标志获取所有app信息
            del self.params["_user"]
            return super().get_model()

        if self.request.user.is_owner():
            appid = owner_app_id(self.request.user.id)
            self.params["id__in"] = appid
            self.select_related = ["types", "usergroup_set__members", "creator"]

        if self.request.user.is_admin():
            self.select_related = ["types", "usergroup_set__members", "creator"]
            self.values_white_list = False
            self.values = ['password', 'is_superuser', 'is_staff', 'date_joined', 'last_connected', '_role']

        if not self.select_related:
            # 兼容普通用户无参数时返回所有app信息
            return super().get_model()

        res = super().get_model()
        i = 0
        while i < len(res["data"]):
            data = res["data"][i]
            if data.get("usergroup_set"):
                j = 0
                while j < len(data["usergroup_set"]):
                    group = data["usergroup_set"][j]
                    if group["type"] == UserGroupType.owner_id() and group["members"]:
                        group["members"] = ",".join([user['username'] for user in group["members"]])
                    else:
                        del data["usergroup_set"][j]
                        j -= 1
                    j += 1
            i += 1
        return res

    @staticmethod
    def _get_app_displaying_task(app_id):
        return GrayTask.objects.filter(app_id=app_id, is_display=True).first()

    @detail_route(url_name='displayingtask', url_path='displayingTask', methods=['get'])
    def to_displaying_task(self, request, pk=None):
        task = self._get_app_displaying_task(pk)
        if not task:
            return Response({'msg': '找不到此app置顶任务'}, status=status.HTTP_404_NOT_FOUND)
        return HttpResponseRedirect(get_task_detail_page_path(task))

    @detail_route(url_name='fileissue', url_path='fileIssue', methods=['get'])
    def to_file_issue(self, request, pk=None):
        task = self._get_app_displaying_task(pk)
        if not task:
            return Response({'msg': '找不到此app置顶任务及反馈问题页面'}, status=status.HTTP_404_NOT_FOUND)
        return HttpResponseRedirect(get_task_file_issue_page_path(task))
