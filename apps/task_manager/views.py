from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, BasePermission, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import GrayTask, GrayAppVersion, GrayStatus, App, IssueExtField
from .serializers import GrayTasksSerializer, GrayStatusSerializer, IssueExtFieldSerializer
from apps.common.models import Image
from apps.common.gated_logger import gated_debug_logger
from apps.user_group.models import UserGroup
from .filters import GrayTaskFilter, IssueExtFieldFilter


class IsAppOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        result = True
        if request.method in ('DELETE', 'PATCH', 'PUT'):
            result = UserGroup.is_owner(request.user, obj.app)
        return result

    def has_permission(self, request, view):
        result = True
        if request.method in ('POST', 'GET') and request.data.get('appId'):
            app = get_object_or_404(App, id=request.data['appId'])
            result = UserGroup.is_owner(request.user, app)

        return result


class GrayTasksViewSet(viewsets.ModelViewSet):
    model = GrayTask
    queryset = GrayTask.objects.order_by("-created_time").all()
    serializer_class = GrayTasksSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAppOwner)
    filter_class = GrayTaskFilter

    @detail_route(methods=["PATCH"])
    def startTest(self, request, pk=None):
        '''
        PATCH: api/v1/tasks/{id}/startTest/
        {
            "currentStep":1,
            "appVersion":{
                "android":{
                    "urlDownload":"http://apphub.ffan.com/api/appdownload/ffan/0/0/develop/4.20.0.0.1848//None/None/Feifan_o2o_4_20_0_0_DEV_1848_2017_07_25_release.apk",
                    "createDate":"2017-07-25",
                    "versionId":"4.20.0.0.1848"
                },
                "ios":{
                    "urlDownload":"http://apphub.ffan.com/api/appdownload/ffan/0/0/develop/4.20.0.0.1848//None/None/Feifan_o2o_4_20_0_0_DEV_1848_2017_07_25_release.apk",
                    "createDate":"2017-07-25",
                    "versionId":"4.20.0.0.1848"
                }
            }
        }
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        app_dict = {}
        param_dict = request.data
        app_version = param_dict.get("appVersion", {})
        android_version = app_version.get("android")
        ios_version = app_version.get("ios")

        if android_version:
            try:
                app_dict['android_version'] = android_version.get("versionId")
                if android_version.get("createDate"):
                    app_dict['android_release_date'] = datetime.strptime(android_version.get("createDate"), '%Y-%m-%d')
            except Exception as e:
                gated_debug_logger.error("{}".format(e))
                raise ValidationError({"msg": "{}".format(e)})
            app_dict['android_download_url'] = android_version.get("urlDownload")
        if ios_version:
            try:
                app_dict['ios_version'] = ios_version.get("versionId")
                if ios_version.get("createDate"):
                    app_dict['ios_release_date'] = datetime.strptime(ios_version.get("createDate"), '%Y-%m-%d')
            except Exception as e:
                gated_debug_logger.error("{}".format(e))
                raise ValidationError({"msg": "{}".format(e)})
            app_dict['ios_download_url'] = ios_version.get("urlDownload")
        app_dict['current_step'] = param_dict.get("currentStep")
        task = self.get_object()
        # 外灰步骤android必须提供--外灰的内容暂时不用
        # if app_dict['current_step'] > task.inner_strategy_steps and (not app_dict['android_version']):
        #     raise ValidationError({'msg': "Outer Strategy must have android version"})

        app_dict['gray_task'] = task
        app_dict['operator'] = request.user

        GrayAppVersion.update_version(app_dict)
        return Response(task.to_dict())

    @detail_route(methods=["PATCH"])
    def isDisplay(self, request, pk=None):
        '''
        PATCH: api/v1/tasks/{id}/isDisplay/
        设置置顶任务，默认值每个app只有一个置顶任务
        置顶任务可以取消，不影响其他app置顶任务
        :param request:
        :param pk:
        :return:
        '''
        is_display = request.data.get("isDisplay", "").lower()
        if is_display.lower() not in ("true", "false"):
            raise ValidationError({'msg': 'isDisplay must be true or false'})
        task = self.get_object()
        task.set_is_display(is_display)
        return Response(task.to_dict())

    @detail_route(methods=["PATCH"])
    def image(self, request, pk=None):
        '''
        PATCH: api/v1/tasks/{id}/image/
        描述：更新灰度任务
        :param request:
        :param pk:
        :return:
        '''
        task = self.get_object()
        image_id = request.data.get("imageId", None)
        try:
            image = get_object_or_404(Image, image_id=image_id)
            task.image = image
            task.save()
        except Exception as e:
            gated_debug_logger.debug("Update task:{} Image Fail ".format(pk))
            raise ValidationError({"msg": "Update image  Fail, %s " % e})

        return Response(task.to_dict())

    @detail_route(methods=["PATCH"])
    def currentStatus(self, request, pk=None):
        '''
        PATCH: api/v1/tasks/{id}/currentStatus/
        描述：设置测试状态
        消息类型："Content-Type": "application/json"
        :param request:
        :param pk:
        :return:
        '''
        task = self.get_object()
        status_name = request.data.get("status")
        status = get_object_or_404(GrayStatus, name=status_name)
        task.update_status(status)

        return Response(task.to_dict())


class GrayStatusView(mixins.ListModelMixin, viewsets.GenericViewSet):
    model = GrayStatus
    queryset = GrayStatus.objects.all()
    serializer_class = GrayStatusSerializer
    permission_classes = (IsAuthenticated,)


class TaskExtendFieldView(viewsets.ModelViewSet):
    model = IssueExtField
    serializer_class = IssueExtFieldSerializer
    permission_classes = (IsAuthenticated,)
    filter_class = IssueExtFieldFilter

    def find_task(self):
        return get_object_or_404(GrayTask, id=self.kwargs.get('task_id'))

    def get_queryset(self):
        return self.model.objects.filter(task_id=self.kwargs.get('task_id'))
