from django.db.models import Sum
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.response import Response
from apps.issue.models import Issue
from apps.task_manager.models import GrayTask
from .filters import UserChartFilter, TaskChartFilter
from .serializers import UserChartSerializer, TaskChartSerializer, TaskDetailChartSerializer


def index_sorted(queryset):
    """
    获取积分与排名的对应关系
    :param queryset
    :return: score_to_index
    """
    score_to_index = dict()
    i = 1
    for L in queryset:
        score_to_index[L['score_sum']] = i
        i += 1
    return score_to_index


class UserChartViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    用户总榜单
    :return
    {
      "status": 200,
      "msg": "成功",
      "data": {
        "total": 1,
        "next": null,
        "previous": null,
        "results": [
          {
            "current": {
              "scoreSum": 7,
              "chineseName": "冯志超-合作方",
              "index": 2,
              "userName": "v_fengzhichao"
            }
          },
          {
            "lists": [
              {
                "scoreSum": 7,
                "chineseName": "冯志超-合作方",
                "index": 2,
                "departmentLevel2": null,
                "userId": 1871,
                "departmentLevel1": null,
                "userName": "v_fengzhichao",
                "issuesCount": 6
              }
            ]
          }
        ]
      }
    }
    """
    model = Issue
    serializer_class = UserChartSerializer
    filter_class = UserChartFilter
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['index'] = index_sorted(self.get_queryset())
        return context

    def get_queryset(self):
        queryset = Issue.objects.values('creator_id').annotate(score_sum=Sum('score')).order_by('-score_sum')
        return queryset

    def list(self, request, *args, **kwargs):
        representation_list = super().list(self, request)
        current_user = dict()
        current_user['current'] = dict()
        all_user = dict()
        all_user['lists'] = []
        for L in representation_list.data['results']:
            # 当前用户参加过众测
            if L['userName'] == self.request.user.username:
                current_user['current']['userName'] = L['userName']
                current_user['current']['chineseName'] = L['chineseName']
                current_user['current']['scoreSum'] = L['scoreSum']
                current_user['current']['index'] = L['index']
                break
        # 当前用户没有参加过众测
        if not current_user['current']:
            current_user['current']['userName'] = self.request.user.username
            current_user['current']['chineseName'] = self.request.user.full_name
            current_user['current']['scoreSum'] = 0
            current_user['current']['index'] = 0
        for L in representation_list.data['results']:
            all_user['lists'].append(L)
        representation_list.data['results'] = []
        representation_list.data['results'].append(current_user)
        representation_list.data['results'].append(all_user)
        return Response(representation_list.data)


class TaskChartViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    任务总榜单，可以按照appId或者appName查询
    :return
    {
      "status": 200,
      "msg": "成功",
      "data": {
        "total": 2,
        "next": null,
        "previous": null,
        "results": [
          {
            "appName": "飞凡APP",
            "issuesCount": 5,
            "taskName": "test text message",
            "endDate": "2017-08-22",
            "taskId": 5,
            "userCount": 3,
            "startDate": "2017-08-15",
            "appDownload": 62,
            "taskDesc": "",
            "index": 1,
            "scoreSum": 112,
            "appId": 1
          },
          {
            "appName": "商户App",
            "issuesCount": 7,
            "taskName": "商户app0811灰度演练测试（sit环境）",
            "endDate": "2017-08-18",
            "taskId": 1,
            "userCount": 3,
            "startDate": "2017-08-11",
            "appDownload": 0,
            "taskDesc": "",
            "index": 2,
            "scoreSum": 8,
            "appId": 2
          }
        ]
      }
    }
    """
    model = Issue
    serializer_class = TaskChartSerializer
    filter_class = TaskChartFilter
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['index'] = index_sorted(self.filter_queryset(self.get_queryset()))
        return context

    def get_queryset(self):
        queryset = Issue.objects.values('task_id', 'app_id').annotate(score_sum=Sum('score')).order_by('-score_sum')
        return queryset


class TaskChartDetailViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    任务详情榜单，显示具体任务下，参与人员的排名情况
    :return
    {
      "status": 200,
      "msg": "成功",
      "data": {
        "total": 3,
        "next": null,
        "previous": "http://127.0.0.1:8080/api/v1/taskChart/5/?page=2&pageSize=1",
        "results": [
          {
            "current": {
              "appName": "飞凡APP",
              "taskName": "test text message",
              "userName": "v_fengzhichao",
              "chineseName": "冯志超-合作方",
              "taskId": 5,
              "appId": 1,
              "scoreSum": 0,
              "index": 0
            }
          },
          {
            "lists": [
              {
                "taskName": "test text message",
                "userName": "liudan71",
                "taskId": 5,
                "scoreSum": 0,
                "appName": "飞凡APP",
                "index": 3,
                "chineseName": "刘丹",
                "departmentLevel2": "产品技术体系",
                "appId": 1,
                "userId": 2149,
                "departmentLevel1": "飞凡信息公司",
                "issuesCount": 1
              }
            ]
          }
        ]
      }
    }
    """
    model = Issue
    serializer_class = TaskDetailChartSerializer
    permission_classes = (IsAuthenticated,)

    def find_task(self):
        task_id = self.kwargs.get('task_id')
        try:
            task = get_object_or_404(GrayTask, id=task_id)
        except ValueError:
            raise Http404('Task with id=%s not found.' % task_id)
        return task.id

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['index'] = index_sorted(self.filter_queryset(self.get_queryset()))
        return context

    def get_queryset(self):
        queryset = Issue.objects.filter(task=self.find_task()). \
            values('creator_id', 'task_id', 'app_id').annotate(score_sum=Sum('score')). \
            order_by('-score_sum')
        return queryset

    def list(self, request, *args, **kwargs):
        representation_list = super().list(self, request)
        current_user = dict()
        current_user['current'] = dict()
        all_user = dict()
        all_user['lists'] = []
        for L in representation_list.data['results']:
            # 当前用户参加过该任务的众测
            if L['userName'] == self.request.user.username:
                current_user['current'] = L
                break
        # 当前用户没有参加过该任务的众测
        if not current_user['current'] and representation_list.data['results']:
            current_user['current']['userName'] = self.request.user.username
            current_user['current']['chineseName'] = self.request.user.full_name
            current_user['current']['scoreSum'] = 0
            current_user['current']['index'] = 0
            current_user['current']['appId'] = representation_list.data['results'][0]['appId']
            current_user['current']['appName'] = representation_list.data['results'][0]['appName']
            current_user['current']['taskId'] = representation_list.data['results'][0]['taskId']
            current_user['current']['taskName'] = representation_list.data['results'][0]['taskName']
        for L in representation_list.data['results']:
            all_user['lists'].append(L)
        representation_list.data['results'] = []
        representation_list.data['results'].append(current_user)
        representation_list.data['results'].append(all_user)
        return Response(representation_list.data)
