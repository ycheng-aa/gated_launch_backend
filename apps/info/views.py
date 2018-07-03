import datetime
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.app.models import App
from apps.award.models import Awardee
from apps.info.serializers import MyTasksSerializer
from apps.issue.models import Issue
from apps.task_manager.models import SnapshotInnerStrategy
from apps.usage.models import EventTracking, EventType, Property
from apps.common.gated_logger import gated_debug_logger
from apps.task_manager.models import GrayTask


class MySummaryView(APIView):
    """
    View to list summary info of user in the system

    * Requires token authentication.
    * All users are able to access this view.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        :param request: token
        :return:
        {
            "status": "200", //服务状态码；若是查询的crator信息不存在，则返回500；
            "msg": "成功",
            "data": {
                "name":"v_fengzhichao",             //用户名称
                "takenTasksCount": 3,               //参与灰度任务次数
                "reportedIssuesCount": 12,          //反馈问题数量
                "awardCount": 2,                    //赢得奖励次数
            }
        }
        """
        user = request.user
        res = dict()
        # 获取用户名称
        username = user.username
        res['name'] = username
        report_issues = Issue.objects.filter(creator=user.pk)

        # 获取参与灰度任务次数
        tasks = set([report.task.pk for report in report_issues if report.task])
        res['takenTasksCount'] = len(tasks)

        # 获取反馈问题数量
        res['reportedIssuesCount'] = report_issues.count()

        # 获取赢得奖励次数
        res['awardCount'] = Awardee.objects.filter(user=user.pk).count()
        return Response(data=res)


class MyAppsView(APIView):
    """
    View to list all apps info of user taken

    * Requires token authentication.
    * All users are able to access this view.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        :param request: token
        :return:
        "data": {
            "total": "3",
            "results": [
                {
                    "id": 3,                            // 应用id
                    "name": "非凡",                       // 项目
                    "imageId": "http://xxxxx/ffan.jpg"   // 图标URL
                },
                {
                    "id": 3,                            // 应用id
                    "name": "非凡",                       // 项目
                    "imageId": "http://xxxxx/ffan.jpg"   // 图标URL
                },
            ]
        }
        """
        user = request.user
        res = dict()

        # 获取用户所有反馈过问题的APP
        report_issues = Issue.objects.filter(creator=user.pk)
        apps = set([report.app.id for report in report_issues if report.app])
        res['total'] = len(apps)
        app_info_array = []
        for aid in apps:
            app_info = dict()
            app = App.objects.get(pk=aid)
            if app:
                app_info['id'] = aid
                app_info['name'] = app.name
                app_info['imageId'] = app.image.pk
                app_info_array.append(app_info)
        res['results'] = app_info_array
        return Response(data=res)


class MyTasksViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    View to list all tasks info of user taken

    * Requires token authentication.
    * All users are able to access this view.
    :return:
          "data": {
            "total": 2,
            "next": null,
            "previous": null,
            "results": [
              {"imageId": "T1_ELvB7Jg1RCvBVdK",
                "taskId": 1,
                "taskCreator": "v_fengzhichao",
                "endDate": "2017-08-18",
                "startDate": "2017-08-11",
                "taskTotalScore": 6,
                "taskName": "商户app0811灰度演练测试（sit环境）",
                "app": "商户App",
                "taskStatus": "已完成"
              },
              {"imageId": "T1mZbvBXLb1RCvBVdK",
                "taskId": 5,
                "taskCreator": "liudan71",
                "endDate": "2017-08-22",
                "startDate": "2017-08-15",
                "taskTotalScore": 1,
                "taskName": "test text message",
                "app": "飞凡APP",
                "taskStatus": "已完成"
              }
            ]
  }
    """
    model = GrayTask
    serializer_class = MyTasksSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # 获取用户关联的内灰策略与task的关联关系(user->group->strategy）
        user = self.request.user
        snapshot_inner_strategies = SnapshotInnerStrategy.objects.filter(user_groups__members=user)
        # 通过以上关联关系，获取task_id_set
        task_id_set = set()

        for inner_strategy in snapshot_inner_strategies:
            task_id_set.add(inner_strategy.gray_task_id)

        queryset = GrayTask.objects.filter(id__in=task_id_set).order_by('-created_time').distinct()
        return queryset


class InfoParamHandlerMixin(object):
    def _param_handler(self, request):
        try:
            app_id = int(request.query_params.get('appId', 0))
            task_id = int(request.query_params.get('taskId', 0))
            link_from = request.query_params.get('linkFrom')
            start_time = request.query_params.get('startTime')
            end_time = request.query_params.get('endTime')
            # 将开始时间和结束时间转换为datetime类型
            if start_time:
                start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
            if end_time:
                end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
                end_time = (end_time + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            return app_id, task_id, link_from, start_time, end_time

        except ValueError as e:
            gated_debug_logger.debug(str(e))
            gated_debug_logger.debug(
                'Get the request param taskId or appId or start_time or end_time is Invalid')
            raise ValueError('Invalid Params: {}'.format(str(e)))


class TakenStatsView(APIView, InfoParamHandlerMixin):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        :param request: token, appId, taskId, linkFrom, startTime, endTime
        :return:
        {
            "status": 200,
            "msg": "成功",
            "data": {
                    "appId": 5,                                  //参数：app id，全表唯一
                    "taskId": 0,                                 //参数：task id，全表唯一
                    "linkFrom": null,                            //参数：参与途径
                    "startTime": null,                           //参数：查询开始时间
                    "endTime": null,                             //参数：查询结束时间
                    "taskDetailEntry": {
                        "userCount": 2,                         //进入任务详情页人数--按照人员去重
                        "eventCount": 70                        //进入任务详情页人次
                        }，
                    "appDownload": {
                        "userCount": 1,                         //下载人数--按照人员去重
                        "eventCount": 19                        //下载人次
                        },
                    "feedbackSubmitSuccess": {
                        "userCount": 0,                         //反馈问题提交成功人数--按照人员去重
                        "eventCount": 0                        //反馈问题提交成功人次
                        }
                    }
        }
        """
        try:
            app_id, task_id, link_from, start_time, end_time = self._param_handler(request)
            if (start_time and not end_time) or (not start_time and end_time):
                gated_debug_logger.error(
                    "startTime and endTime must be provided at the same time")
                raise Exception('startTime and endTime must be provided at the same time')
            if app_id and task_id:
                gated_debug_logger.error(
                    "appId and taskId can not be provided at the same time")
                raise Exception('appId and taskId can not be provided at the same time')
        except ValueError as e:
            return Response(data={'results': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        res = {'appId': app_id, 'taskId': task_id, 'linkFrom': link_from, 'startTime': start_time, 'endTime': end_time}
        for event in ['taskDetailEntry', 'appDownload', 'feedbackSubmitSuccess']:
            # 获取要统计的事件的事件id
            event_type = EventType.objects.get(name=event)
            # 没有时间要求，直接按事件类型查询事件id_list
            if not start_time and not end_time:
                id_list = EventTracking.objects.values('id').filter(type=event_type)
            # 有时间要求，按照时间过滤id_list
            if start_time and end_time:
                id_list = EventTracking.objects.values('id').filter(type=event_type).filter(
                    created_time__range=(start_time, end_time))
            # 如果appId和taskId都没有传，上面所得id_ist不需要按照appId或者taskId过滤
            # 按照app维度查询，按照appId过滤id_list
            if app_id != 0:
                id_list = Property.objects.values('event_id').filter(event__in=id_list).filter(
                    key='appId', value=app_id)
            # 按照task维度查询，按照taskId过滤id_list
            if task_id != 0:
                id_list = Property.objects.values('event_id').filter(event__in=id_list).filter(
                    key='taskId', value=task_id)
            # 如果没有要求来源，直接计算人数和人次
            if not link_from:
                user_count = EventTracking.objects.filter(id__in=id_list).distinct().values(
                    "user_id").count()
                event_count = len(id_list)
            # 如果要求来源，再在property表中过滤一次from，之后，再计算人数和人次
            else:
                id_list = Property.objects.values('event_id').filter(event__in=id_list).filter(
                    key='from',
                    value=link_from)
                user_count = EventTracking.objects.filter(id__in=id_list).distinct().values("user_id").count()
                event_count = len(id_list)
            res[event] = {'userCount': user_count, 'eventCount': event_count}
        return Response(data=res)


class WeiXinLogInStatsView(APIView, InfoParamHandlerMixin):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        :param request: token, startTime, endTime
        :return:
        {
            "status": 200,
            "msg": "成功",
            "data": {
                    "startTime": null,                                       //参数：查询开始时间
                    "endTime": null,                                        //参数：查询结束时间
                    "wxLoginEntry": [
                      {
                        "departments": "飞凡信息公司/产品技术体系/共享服务产研群/技术支撑产研中心/质量管理部",
                        "userName": "liqianyang",
                        "userId": 7040,
                        "loginTime": "2017-10-23T08:58:32.541300"
                        },
                     {
                        "departments": "飞凡信息公司/产品技术体系/共享服务产研群/技术支撑产研中心/质量管理部",
                        "userName": "liqianyang",
                        "userId": 7040,
                        "loginTime": "2017-10-23T16:00:39.526991"
                    }
                    ]
                    }
        }
        """
        app_id, task_id, link_from, start_time, end_time = self._param_handler(request)

        queryset = EventTracking.objects.filter(type__name="wxLoginEntry")
        if start_time:
            queryset = queryset.filter(created_time__gt=start_time)
        if end_time:
            queryset = queryset.filter(created_time__lt=end_time)
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
        end_time = (end_time + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
        res = {'startTime': start_time, 'endTime': end_time}
        res["wxLoginEntry"] = []
        for event_tracking in queryset:
            dict = {}
            dict["userId"] = event_tracking.user.id
            dict["userName"] = event_tracking.user.username
            dict["loginTime"] = event_tracking.created_time
            dict['departments'] = "/".join([dep.name for dep in event_tracking.user.departments])
            res["wxLoginEntry"].append(dict)
        return Response(data=res)
