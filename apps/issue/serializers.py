# -*- coding: utf-8 -*-
import json
from django.db import transaction
import requests
from rest_framework import serializers, status
from apps.auth.models import User
from apps.common.fields import CreatableSlugField
from apps.common.gated_logger import gated_debug_logger
from apps.common.serializers import AuthedSerializer
from gated_launch_backend.settings import JIRA_SEVERITY_TO_ZC_SCORE, WEIXIN_REPORT_SOURCE_FLAG, JIRA_BROWSE_URL
from apps.utils.utils import gen_params, is_issue_from_weixin, generate_change_log, may_send_wechat_notification
from gated_launch_backend.settings import JIRA_API_URL
from .models import Issue, IssueStatus, IssueType, BusinessModuleTree, PhoneBrand, Region, \
    IssueReportSource, IssuePriority, IssueExtValue
from apps.app.models import App
from apps.task_manager.models import GrayTask, IssueExtField
from apps.common.models import AppModule, Image


class IssueTypeSerializer(AuthedSerializer):
    class Meta:
        model = IssueType
        fields = ('id', 'name')


class IssueStatusSerializer(AuthedSerializer):
    class Meta:
        model = IssueStatus
        fields = ('id', 'name')


class BusinessModuleSerializer(AuthedSerializer):
    parent = serializers.CharField(source='parent.name', required=False, read_only=True)
    parentId = serializers.PrimaryKeyRelatedField(source='parent', required=False, read_only=True)

    class Meta:
        model = BusinessModuleTree
        fields = ('id', 'name', 'level', 'parent', 'parentId', 'disabled')


class PhoneBrandSerializer(AuthedSerializer):
    class Meta:
        model = PhoneBrand
        fields = ('id', 'name')


class RegionSerializer(AuthedSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')


class ExtensionField(serializers.Field):
    def to_internal_value(self, data):
        return data


class IssueSerializer(AuthedSerializer):
    creator = serializers.CharField(source='creator.username', required=False, read_only=True)
    marker = serializers.CharField(source='marker.username', required=False, read_only=True)
    images = serializers.PrimaryKeyRelatedField(many=True, queryset=Image.objects.all(), required=False)
    jiraId = serializers.CharField(source='jira_link', allow_blank=True, required=False, max_length=100)
    appId = serializers.SlugRelatedField(source='app', slug_field='id', queryset=App.objects.all())
    taskId = serializers.SlugRelatedField(source='task', slug_field='id', queryset=GrayTask.objects.all())
    issueModuleId = serializers.SlugRelatedField(source='app_module', slug_field='id', queryset=AppModule.objects.all(),
                                                 required=False, allow_null=True)
    statusId = serializers.SlugRelatedField(source='status', slug_field='id', queryset=IssueStatus.objects.all(),
                                            required=False, allow_null=True)
    typeId = serializers.SlugRelatedField(source='type', slug_field='id', queryset=IssueType.objects.all(),
                                          required=False, allow_null=True)
    appName = serializers.SlugRelatedField(source='app', slug_field='name', required=False, read_only=True)
    appImageId = serializers.SlugRelatedField(source='app.image', slug_field='image_id', required=False, read_only=True)
    taskName = serializers.SlugRelatedField(source='task', slug_field='task_name', required=False, read_only=True)
    issueModuleName = serializers.SlugRelatedField(source='app_module', slug_field='module_name', required=False,
                                                   read_only=True)
    statusName = serializers.SlugRelatedField(source='status', slug_field='name', required=False, read_only=True)
    typeName = serializers.SlugRelatedField(source='type', slug_field='name', required=False, read_only=True)
    reportSource = CreatableSlugField(source='report_source', slug_field='name',
                                      queryset=IssueReportSource.objects.all(), required=False)
    createdAt = serializers.DateTimeField(source='created_time', required=False, read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_time', required=False, read_only=True)
    priority = serializers.SlugRelatedField(slug_field='desc', queryset=IssuePriority.objects.all(),
                                            required=False, allow_null=True)
    score = serializers.CharField(required=False)
    remindKSTFlag = serializers.NullBooleanField(source='kst_unread_flag', required=False)
    remindPlatFlag = serializers.NullBooleanField(source='plat_unread_flag', required=False)
    zcChangeLogs = serializers.CharField(source='zc_change_logs', required=False)
    extFields = ExtensionField(required=False)
    componentName = serializers.SlugRelatedField(source='app.component', slug_field='name', read_only=True)
    operator = serializers.SlugRelatedField(slug_field='username', required=False,
                                            allow_null=True, queryset=User.objects.all())

    class Meta:
        model = Issue
        fields = ('id', 'appId', 'taskId', 'title', 'detail', 'images',
                  'score', 'jiraId', 'issueModuleId', 'statusId', 'typeId',
                  'creator', 'marker', 'createdAt', 'updatedAt',
                  'appName', 'taskName', 'issueModuleName', 'statusName',
                  'typeName', 'appImageId', 'reportSource', 'other', 'priority',
                  'remindKSTFlag', 'remindPlatFlag', 'zcChangeLogs', 'extFields',
                  'componentName', 'operator')

    def _validate_extended_fields(self, task, ext_fields_info):
        if not task:
            # should not no task_id, but other parts will handle this
            return
        if self.instance and not ext_fields_info:
            # update但是没有扩展字段内容
            return
        must_have_fields = set([])
        all_legal_fields = set([])
        for field in task.ext_fields.all():
            all_legal_fields.add(field.name)
            if not field.is_optional:
                must_have_fields.add(field.name)
        incoming_fields = set(ext_fields_info.keys()) if ext_fields_info else set([])
        if incoming_fields - all_legal_fields:
            # 不能多
            serializers.ValidationError({'msg': '{} 为非法扩展字段名'.format(incoming_fields - all_legal_fields)})
        if must_have_fields - incoming_fields:
            # 不能少
            raise serializers.ValidationError(
                {'msg': '缺少以下必须扩展字段: {}'.format(must_have_fields - incoming_fields)})

    def validate(self, data):
        super().validate(data)
        task = data.get('task')
        if not task and self.instance:
            task = self.instance.task
        self._validate_extended_fields(task, data.get('extFields'))
        return data

    def _create_or_update_extended_fields(self, issue, ext_fields_info, is_update=False):
        if not ext_fields_info:
            return
        if is_update:
            IssueExtValue.objects.filter(issue=issue).delete()
        for field, value in ext_fields_info.items():
            IssueExtValue.objects.create(issue=issue,
                                         field=IssueExtField.objects.get(name=field, task=issue.task),
                                         value=value)

    def create(self, validated_data):
        validated_data['creator'] = self.current_user()
        if ('report_source' in dict(validated_data).keys()) and str(
                validated_data['report_source']) == WEIXIN_REPORT_SOURCE_FLAG:
            validated_data['score'] = JIRA_SEVERITY_TO_ZC_SCORE.get(validated_data.get('score', '严重'),
                                                                    JIRA_SEVERITY_TO_ZC_SCORE['严重'])
        else:
            validated_data['score'] = 0
        validated_data['status'] = IssueStatus.objects.get(name=IssueStatus.NEW_STATUS)
        if 'priority' not in validated_data:
            validated_data['priority'] = IssuePriority.get_default_obj()
        ext_fields_info = validated_data.pop('extFields', None)
        with transaction.atomic():
            instance = super().create(validated_data)
            self._create_or_update_extended_fields(instance, ext_fields_info)

        return instance

    def update(self, instance, validated_data):
        jira_id = instance.jira_link
        if not jira_id:
            user = self.current_user()
            generate_change_log(instance, validated_data, user)
        ext_fields_info = validated_data.pop('extFields', None)
        prev_status = instance.status
        with transaction.atomic():
            super().update(instance, validated_data)
            self._create_or_update_extended_fields(instance, ext_fields_info, True)
        # 微信问题不管是否转jira，只要通过众测平台有update，kst_unread_flag置True
        if is_issue_from_weixin(instance) and not instance.kst_unread_flag:
            instance.kst_unread_flag = True
            instance.save()

        # if issue has jira_id then update to jira
        if jira_id:
            params = gen_params(instance)
            result = requests.put(JIRA_API_URL + jira_id + '/', params)
            if result.json().get("status") == status.HTTP_200_OK:
                comments = result.json().get("data", {}).get("comments", "")
                change_log = result.json().get("data", {}).get("changeLog", "")
                # 微信问题和众测问题非首次更新时，other字段不为空，需要更新原有other
                if instance.other:
                    other_json = json.loads(instance.other)
                    other_json.update({"comments": comments, "changeLog": change_log})
                # 由于众测问题首次更新时，other字段为空，直接赋值
                else:
                    other_json = {"comments": comments, "changeLog": change_log}
                instance.other = json.dumps(other_json)
                instance.save()
                res = "Update jira %s successfully!" % jira_id
                gated_debug_logger.debug(msg=res)
            else:
                res = "Update jira %s failed! error msg: %s" % (jira_id, result.text)
                gated_debug_logger.error(msg=res)

        # 根据最终数据决定是否发送微信提醒
        may_send_wechat_notification(prev_status, instance, self.current_user())
        return instance

    def to_representation(self, value):
        results = super().to_representation(value)
        results['departments'] = "/".join([dep.name for dep in value.creator.departments])
        results['jiraLink'] = JIRA_BROWSE_URL.format(results['jiraId']) if results['jiraId'] else ""
        results['extFields'] = dict((ext.field.name, ext.value) for ext in value.ext_values.all())
        default_operator = value.app.component.operator.username
        if value.jira_link and value.operator:
            results['operator'] = value.operator.username if value.operator.username else default_operator
        else:
            results['operator'] = default_operator
        return results


class IssueLiteSerializer(AuthedSerializer):
    jiraId = serializers.CharField(source='jira_link', read_only=True)
    statusName = serializers.CharField(source='status.name', read_only=True)
    createdAt = serializers.DateTimeField(source='created_time', read_only=True)
    remindKSTFlag = serializers.NullBooleanField(source='kst_unread_flag', required=False, read_only=True)
    remindPlatFlag = serializers.NullBooleanField(source='plat_unread_flag', required=False, read_only=True)

    class Meta:
        model = Issue
        fields = ('id', 'jiraId', 'statusName', 'title', 'createdAt', 'other', 'score',
                  'remindKSTFlag', 'remindPlatFlag')
