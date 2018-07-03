import json
import traceback
from django.db.models import Q, Count
import requests
from json import JSONDecodeError
from rest_framework.decorators import detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions, status
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from django.contrib.auth import get_user_model
from apps.common.exceptions import JiraError
from apps.info.views import InfoParamHandlerMixin
from apps.usage.models import EventTracking, Property
from apps.utils.utils import zc_set_jira_status, is_issue_from_weixin, gen_params, issue_update, \
    get_model_object_from_cache, set_model_object_to_cache, get_from_cache, set_to_cache, update_model_obj, \
    is_app_owner, generate_change_log, format_comment, update_issue_comment, may_log_exception_to_sentry, \
    jira_issue_is_avaliable, try_delete_from_statplat
from .models import Issue, IssueStatus, IssueType, BusinessModuleTree, PhoneBrand, Region
from apps.user_group.models import UserGroup
from apps.app.models import App
from apps.common.gated_logger import gated_debug_logger
from apps.common.tasks import send_sms_task
from .serializers import IssueSerializer, IssueStatusSerializer, IssueTypeSerializer, BusinessModuleSerializer, \
    PhoneBrandSerializer, RegionSerializer, IssueLiteSerializer
from .filters import IssueFilter
from gated_launch_backend.settings import JIRA_API_URL, WEIXIN_REPORT_SOURCE_FLAG, JIRA_ZC_USER, KE_SU_TONG


class IsAppOwner(permissions.BasePermission):
    """
        used for model Issue
        对于Issue来说，只有APP管理员能进行删、修改某些字段（score/jira_link/status/type）
    """

    def has_permission(self, request, view):
        result = True
        if request.method == 'GET' and 'pk' not in view.kwargs:
            if 'appId' in request.query_params:
                app_lists = App.objects.values_list('id', flat=True)
                if not request.query_params['appId'].isdigit() or int(request.query_params['appId']) not in app_lists:
                    return result
                app = App.objects.get(pk=request.query_params['appId'])
                if not UserGroup.is_owner(request.user, app) and 'creator' in request.query_params and \
                        request.query_params['creator'] != request.user.username:
                    result = False
            elif 'creator' not in request.query_params or request.query_params['creator'] != request.user.username:
                result = False

        return result

    def has_object_permission(self, request, view, obj):
        result = True
        if request.method == 'DELETE':
            if not UserGroup.is_owner(request.user, obj.app):
                result = False
        elif request.method in ('PATCH', 'PUT'):
            if ('score' in request.data or 'jira_link' in request.data or
                    'status' in request.data or 'type' in request.data) and not \
                    UserGroup.is_owner(request.user, obj.app):
                result = False
        elif request.method == 'GET':
            if not UserGroup.is_owner(request.user, obj.app) and request.user != obj.creator:
                result = False

        return result


class IsPlatOwner(permissions.BasePermission):
    """
        used for model IssueType
        对于IssueType来说，只有平台管理员能进行增删改
    """

    def has_permission(self, request, view):
        result = True
        if request.method in ('POST', 'DELETE', 'PATCH', 'PUT'):
            if not request.user.is_admin():
                result = False
        return result


class IssueTypeViewSet(viewsets.ModelViewSet):
    model = IssueType
    queryset = IssueType.objects.all()
    serializer_class = IssueTypeSerializer
    permission_classes = (IsAuthenticated, IsPlatOwner)


class IssueStatusViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    model = IssueStatus
    queryset = IssueStatus.objects.all()
    serializer_class = IssueStatusSerializer
    permission_classes = (IsAuthenticated,)


class BusinessModuleViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    model = BusinessModuleTree
    queryset = BusinessModuleTree.objects.all().order_by('-id')
    serializer_class = BusinessModuleSerializer
    permission_classes = (IsAuthenticated,)


class PhoneBrandViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    model = PhoneBrand
    queryset = PhoneBrand.objects.all()
    serializer_class = PhoneBrandSerializer
    permission_classes = (IsAuthenticated,)


class RegionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    model = Region
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = (IsAuthenticated,)


class IssueViewSet(viewsets.ModelViewSet):
    model = Issue
    queryset = Issue.objects.all().select_related('task', 'app', 'app_module', 'creator', 'status', 'type', 'marker',
                                                  'report_source', 'priority').prefetch_related('images')
    serializer_class = IssueSerializer
    permission_classes = (IsAuthenticated,)
    filter_class = IssueFilter

    def perform_update(self, serializer):

        issue = self.get_object()
        score = issue.score
        status = issue.status
        serializer.save()

        issue.refresh_from_db()

        # non-wechat issue and score/status changed
        need_send_sms = ((score != issue.score or status != issue.status) and
                         not (issue.report_source and issue.report_source.name == WEIXIN_REPORT_SOURCE_FLAG))
        if need_send_sms:
            user_name = issue.creator.full_name
            issue_title = issue.title
            zc_plat_url = '%s://%s' % (self.request.scheme, self.request.get_host())
            gated_debug_logger.debug(zc_plat_url)
            user_mobile = issue.creator.phone
            sms_msg = '【%s】您反馈的%s问题状态为%s, 得分%s分。请登录飞凡众测平台查看更多细节：%s' % (user_name,
                                                                       issue_title, issue.status,
                                                                       issue.score, zc_plat_url)
            if user_mobile:
                send_sms_task([user_mobile], sms_msg)

    @staticmethod
    def _update_issue_change_log(issue, change_log):
        change_log_field = 'changeLog'
        jira_info = issue.other
        if jira_info:
            jira_info_dict = json.loads(jira_info)
            jira_info_dict[change_log_field] = change_log
        else:
            jira_info_dict = {change_log_field: change_log}

        issue.other = json.dumps(jira_info_dict)
        issue.save()

        return jira_info_dict[change_log_field]

    @detail_route(url_name='jiracomment', url_path='jiraComments', methods=['post'])
    def append_jira_comment(self, request, pk=None):
        issue = self.get_object()
        conclusion = request.data.get('conclusion')
        comment = request.data.get('comment')
        kst = request.data.get('from', "")
        form_id = request.data.get('formId')
        status_code = status.HTTP_400_BAD_REQUEST
        issue_status = issue.status.name

        if not (conclusion or comment):
            result = {'msg': "字段 'conclusion' 和 'comment' 至少要有一个"}
        else:
            try:
                # need to sync to JIRA
                comments = change_log = []
                if issue.jira_link:
                    if not jira_issue_is_avaliable(issue.jira_link):
                        # jira上issue已删除，去除对应JIRA ID.并在接下去按照没有JIRA ID
                        # 的情况尝试处理
                        issue.jira_link = None
                        issue.save()
                    else:
                        issue_status, change_log = zc_set_jira_status(issue.jira_link, flag=conclusion, comment=comment)
                        issue.status = IssueStatus.objects.get(name=issue_status)
                        # save new status first, even update comments failed
                        issue.save()
                        change_log = self._update_issue_change_log(issue, change_log)
                # if no jira_link，but issue from weixin, need to set the status of issue
                if not issue.jira_link and is_issue_from_weixin(issue):
                    if conclusion == "验证通过":
                        issue_status = "关闭"
                    if conclusion == "验证不通过":
                        issue_status = "处理中"
                    issue.status = IssueStatus.objects.get(name=issue_status)
                    issue.save()
                if comment:
                    new_comment = format_comment(self.request.user, comment)
                    comments = update_issue_comment(issue, new_comment, kst)
                if form_id and not issue.set_ext_field_value('formId', form_id):
                    gated_debug_logger.error('set form id failed for issue {}'.format(issue.id))

                result = {'comments': comments, 'status': issue_status, 'changeLog': change_log}
                status_code = status.HTTP_200_OK

            except JiraError as e:
                result = {'msg': "Jira 错误： {}".format(str(e))}
            except (ValueError, JSONDecodeError) as e:
                result = {'msg': format(str(e))}
        return Response(result, status=status_code)

    disable_kst_unread_flag = 'disable_kst_unread_flag'
    disable_plat_unread_flag = 'disable_plat_unread_flag'

    def _need_change_notify_flag(self, creator_name, current_kst_flag, app_id, jira_id, current_plat_flag,
                                 current_user, request_from):
        if request_from == KE_SU_TONG:
            if creator_name == current_user.username and current_kst_flag:
                return self.disable_kst_unread_flag
        else:
            if not jira_id and is_app_owner(current_user, app_id) and current_plat_flag:
                return self.disable_plat_unread_flag
        return False

    def _save_flag_to_model(self, flag, issue):
        if flag == self.disable_kst_unread_flag:
            issue.kst_unread_flag = False
        if flag == self.disable_plat_unread_flag:
            issue.plat_unread_flag = False
        issue.save()
        return issue

    def get_object(self):
        """
        Basically the generic view's implementation,
        except don't let query params take effect
        """

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(self.get_queryset(), **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = self.request.user
        request_from = request.GET.get('from', "")
        obj_data = get_model_object_from_cache(self.model, pk)
        if obj_data:
            # already got last response data from cache
            flag = self._need_change_notify_flag(obj_data.get('creator'), obj_data.get('remindKSTFlag'),
                                                 obj_data.get('appId'), obj_data.get('jiraId'),
                                                 obj_data.get('remindPlatFlag'),
                                                 user, request_from)
            if flag:
                instance = self.get_object()
                self._save_flag_to_model(flag, instance)
                serializer = self.get_serializer(instance)
                obj_data = serializer.data
                try:
                    set_model_object_to_cache(self.model, pk, obj_data)
                except Exception as e:
                    may_log_exception_to_sentry(str(e))

            try:
                # make sure the cache data can really work
                return Response(obj_data)
            except Exception as e:
                may_log_exception_to_sentry(str(e))

        # get issue data from db
        instance = self.get_object()
        flag = self._need_change_notify_flag(instance.creator.username, instance.kst_unread_flag,
                                             instance.app.id, instance.jira_link,
                                             instance.plat_unread_flag,
                                             user, request_from)
        if flag:
            self._save_flag_to_model(flag, instance)
        serializer = self.get_serializer(instance)
        obj_data = serializer.data
        try:
            set_model_object_to_cache(self.model, pk, obj_data)
        except Exception as e:
            may_log_exception_to_sentry(str(e))

        return Response(obj_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        try:
            set_model_object_to_cache(self.model, serializer.data['id'], serializer.data)
        except Exception as e:
            may_log_exception_to_sentry(str(e))
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        issue_id = instance.id
        jira_id = instance.jira_link
        if jira_id and jira_issue_is_avaliable(jira_id):
            return Response(data={'msg': '请先从JIRA删除此问题'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        try_delete_from_statplat(issue_id, jira_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueLiteViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    model = Issue
    queryset = Issue.objects.all().select_related('status')
    serializer_class = IssueLiteSerializer
    permission_classes = (IsAuthenticated,)
    filter_class = IssueFilter
    cache_timeout = 60 * 10

    @staticmethod
    def _qualified_cached_query_keys():
        return ['creator', 'appId', 'taskId', 'reportSource', 'statusNameOrder']

    def _gen_cache_key(self, request):
        result = ''
        for k in self._qualified_cached_query_keys():
            if k not in request.query_params:
                return None
            v = request.query_params[k]
            if isinstance(v, list):
                if len(v) != 1:
                    return None
                v = v[0]
            result += '{}:'.format(v)
        return result

    def _is_qualified_query_for_cache(self, request):
        return set(request.query_params.keys()) == set(self._qualified_cached_query_keys())

    def _may_get_from_cache(self, request):
        result = None
        try:
            if self._is_qualified_query_for_cache(request):
                cache_key = self._gen_cache_key(request)
                if cache_key:
                    result = get_from_cache(cache_key)
        except Exception as e:
            may_log_exception_to_sentry(traceback.format_exc())
        return result

    def _may_set_to_cache(self, request, data):
        try:
            if self._is_qualified_query_for_cache(request):
                cache_key = self._gen_cache_key(request)
                if cache_key:
                    set_to_cache(cache_key, data, self.cache_timeout)
        except Exception as e:
            may_log_exception_to_sentry(traceback.format_exc())

    def list(self, request, *args, **kwargs):
        cache_result = self._may_get_from_cache(request)
        if cache_result:
            return Response(cache_result)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            self._may_set_to_cache(request, response.data)
            return response

        serializer = self.get_serializer(queryset, many=True)
        self._may_set_to_cache(request, serializer.data)
        return Response(serializer.data)


class IssueStatsView(APIView, InfoParamHandlerMixin):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def _filter_issues_with_issue_from(issue_list, issue_from):
        if not issue_list or not issue_from:
            return issue_list
        id_list = [issue.id for issue in issue_list]
        submit_event_type = 'feedbackSubmitSuccess'
        events_queryset = EventTracking.objects.filter(type__name=submit_event_type). \
            filter(Q(properties__key='issueId', properties__value__in=id_list) |
                   Q(properties__key='from', properties__value=issue_from)).distinct(). \
            values('id').annotate(property_count=Count('properties')).filter(property_count=2)
        event_id_list = [event['id'] for event in events_queryset]
        app_id_from_property = set([])
        if event_id_list:
            for p in Property.objects.filter(event__in=event_id_list, key='issueId'):
                try:
                    app_id_from_property.add(int(p.value))
                except ValueError:
                    pass
        return [issue for issue in issue_list if issue.id in app_id_from_property]

    def get(self, request):
        """
        :param request:
            appId: app id
            taskId: task id
            creatorId: creator id
            reportSourceId: report_source id
            startTime: 2017-10-11
            endTime: 2017-10-13
            issueFrom: 'issue from' info from event tracking

        :return:
          {
              "status": 200,
              "msg": "成功",
              "data": {
                "taskId": 5,
                "totalIssues": 5,
                "validIssues": 5,
                "creatorId" :2,
                "reportSource" :"四大区运营",
                "appName": "飞凡APP",
                "appId": 1,
                "taskName": "test1",
                "results": {
                  "typeStats": {
                    "优化问题": 1
                  },
                  "statusStats": {
                    "handling": 1,
                    "suspending": 4
                  },
                  "moduleStats": {
                    "test2": 2,
                    "test1": 2,
                    "登录": 1
                  }
                }
              }
          }
        """

        try:
            app_id, task_id, _, start_time, end_time = self._param_handler(request)
            report_source = request.query_params.get('reportSource')
            creator_id = int(request.query_params.get('creatorId', 0))
            issue_from = request.query_params.get('issueFrom')
        except ValueError as e:
            return Response(data={'results': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Issue.objects.select_related('status', 'app_module').all()
        if creator_id != 0:
            queryset = queryset.filter(creator_id=creator_id)
        if report_source:
            queryset = queryset.filter(report_source__name=report_source)

        if start_time:
            queryset = queryset.filter(created_time__gt=start_time)
        if end_time:
            queryset = queryset.filter(created_time__lt=end_time)

        if app_id:
            queryset = queryset.filter(app_id=app_id)
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        issue_list = list(queryset)
        issue_list = self._filter_issues_with_issue_from(issue_list, issue_from)

        res = {'totalIssues': len(issue_list), 'validIssues': len([issue for issue in issue_list if issue.score > 0])}
        ret = dict()
        if issue_list:
            issue_status_statistics = {}
            issue_type_statistics = {}
            issue_module_statistics = {}
            not_available_status = 'N/A'
            for issue in issue_list:
                if issue.status:
                    issue_status_statistics[issue.status.description] = issue_status_statistics.get(
                        issue.status.description, 0) + 1
                else:
                    issue_status_statistics[not_available_status] = \
                        issue_status_statistics.get(not_available_status, 0) + 1
                if issue.type:
                    issue_type_statistics[issue.type.name] = issue_type_statistics.get(issue.type.name, 0) + 1
                if issue.app_module:
                    issue_module_statistics[issue.app_module.module_name] = issue_module_statistics.get(
                        issue.app_module.module_name, 0) + 1

            ret['statusStats'] = issue_status_statistics
            ret['typeStats'] = issue_type_statistics
            if task_id != 0 or app_id != 0:
                ret['moduleStats'] = issue_module_statistics
            if task_id:
                res['taskId'] = task_id
                if issue:
                    res['taskName'] = issue.task.task_name
            if app_id:
                res['appId'] = app_id
                if issue:
                    res['appName'] = issue.app.name
            if creator_id:
                res['creatorId'] = creator_id
                res['creator'] = issue.creator.username
            if report_source:
                res['reportSourceName'] = issue.report_source.name
            if issue_from:
                res['issueFrom'] = issue_from
        res['results'] = ret
        return Response(data=res)


class CreateJiraView(APIView):
    def get(self, request):
        user = self.request.user
        issue_id = request.query_params.get('issueId', 0)

        issue = Issue.objects.filter(id=issue_id).first()
        res = dict()
        err_msg = None
        if not issue:
            return Response(data={'msg': 'Params Invalid'}, status=status.HTTP_400_BAD_REQUEST)

        res['issueId'] = issue.id
        if issue.jira_link:
            res['jiraId'] = issue.jira_link
            res['jiraStatus'] = issue.status.name
            return Response(data=res)
        try:
            params = gen_params(issue)
            response = requests.post(JIRA_API_URL, params).json()
            if response.get('status') == status.HTTP_200_OK:
                jira_id = response.get('data', {}).get('jiraId')
                jira_status = response.get('data', {}).get('status', IssueStatus.CREATE_STATUS)
                jira_operator = response.get('data', {}).get('operator')
                operator = get_user_model().objects.get_or_create(username=jira_operator)[0] if jira_operator \
                    else issue.operator
                res['jiraStatus'] = jira_status
                if jira_id:
                    # 将jiraId写回 issue
                    update_value = {'jira_link': jira_id, 'operator': operator,
                                    'status': IssueStatus.objects.get(name=jira_status)}

                    res['jiraId'] = jira_id
                    change_log = response.get('data', {}).get('changeLog', "")
                    if is_issue_from_weixin(issue):
                        other_json = json.loads(issue.other)
                        components = response.get('data', {}).get('components', "")
                        solve_type = response.get('data', {}).get('solveType', "")
                        other_json.update({'solveType': solve_type, 'components': components, 'changeLog': change_log})
                    # 非微信问题，仅回写changeLog
                    else:
                        if issue.other:
                            other_json = json.loads(issue.other)
                            other_json.update({'changeLog': change_log})
                        else:
                            other_json = {'changeLog': change_log}
                    update_value.update({'other': json.dumps(other_json)})
                    generate_change_log(issue, {'jira_link': jira_id}, user)
                    update_model_obj(issue, **update_value)
                    # issue的初始comments写入jira
                    if issue.other:
                        comments_list = []
                        comments = json.loads(issue.other).get('comments', "")
                        if comments:
                            for comment in comments:
                                comments_list.insert(0, comment.get('info', ""))
                            for comment in comments_list:
                                zc_set_jira_status(jira_id, None, comment)
                    return Response(data=res)
                else:
                    err_msg = 'Create JIRA FAILED. No JIRA ID'
            else:
                err_msg = 'Create JIRA FAILED. JIRA service returned \'{}\' with status code {}'.\
                    format(response.get('msg'), response.get('status'))
        except JiraError as e:
            err_msg = "Jira 错误： {}".format(str(e))
        except Exception as e:
            err_msg = format(e)
        return Response({'msg': err_msg}, status=status.HTTP_400_BAD_REQUEST)


class jiraToIssue(APIView):
    """
    jira同步到众测接口
    :param jira_request (jira_request是在jira上配置了webhook，当问题update后，推送出来的json格式消息)
    :return {
              "status": 200,
              "msg": "成功",
              "data": {
                "issueId": 1,
                "jiraId": "CC-80"
              }
            }
    """

    def post(self, request):
        gated_debug_logger.info('jiraToIssue data: {}'.format(request.data))
        jira_id = request.data.get('issue', {}).get('key')
        res = {
            "jiraId": jira_id,
            "issueId": None
        }
        issue = Issue.objects.filter(jira_link=jira_id).first()
        if issue:
            res["issueId"] = issue.id
            result = requests.get(JIRA_API_URL + jira_id + '/')
            if result.json().get('status') == status.HTTP_200_OK:
                params = result.json().get('data')
                status_name = params.get('status')
                # jira的更新user 为zhongce公众号，如果前后状态一样，则表示众测推送的更新引起的jira更新，因此不再处理
                if request.data.get('user', {}).get('name') == JIRA_ZC_USER and status_name == issue.status.name:
                    return Response(res)
                res = issue_update(jira_id, issue, params)
            else:
                gated_debug_logger.info('jiraToIssue get {} failed'.format(JIRA_API_URL + jira_id + '/'))
        return Response(res)
