import datetime
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers

from apps.app.models import App
from apps.auth.models import Department
from apps.common.serializers import AuthedSerializer
from apps.utils.utils import may_create_user_and_depts
from .models import UserGroup, UserGroupType


class UserGroupSerializer(AuthedSerializer):
    type = serializers.SlugRelatedField(slug_field='name', queryset=UserGroupType.objects.all())
    createdAt = serializers.DateTimeField(source='created_time', required=False, read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_time', required=False, read_only=True)
    appName = serializers.CharField(source='app.name', required=False, read_only=True)
    appId = serializers.SlugRelatedField(source='app', slug_field='id', queryset=App.objects.all(),
                                         required=False, default=None)
    memberCount = serializers.IntegerField(source='members.count', required=False, read_only=True)
    creator = serializers.CharField(source='creator.username', required=False, read_only=True)

    def create(self, validated_data):
        validated_data['creator'] = self.current_user()
        instance = super().create(validated_data)
        return instance

    def validate(self, data):
        """
        validate according to business logic
        """
        app = data.get('app')
        group_type = data.get('type')
        if self.instance:
            # put or patch
            if (app and app != self.instance.app) or (group_type and group_type != self.instance.type):
                raise serializers.ValidationError('只允许修改用户群组名称')
            app = self.instance.app
            group_type = self.instance.type
        self._validate_company_group(app, group_type)
        self._validate_angel_group(app, group_type)
        self._validate_custom_group(app, group_type)
        self._validate_owner_group(app, group_type)

        return data

    def _validate_company_group(self, app, group_type):
        if group_type.name == UserGroupType.COMPANY:
            if app:
                raise serializers.ValidationError({'msg': '集团用户不属于具体app，不需要appId参数'})
            if UserGroup.objects.filter(type__name=group_type.name).count() and self.get_method() == 'POST':
                raise serializers.ValidationError('集团用户已存在')
            if not self.current_user().is_admin():
                raise PermissionDenied({'msg': '只有平台管理员才能够创建/修改集团用户群组'})

    def _validate_angel_group(self, app, group_type):
        if group_type.name == UserGroupType.ANGEL:
            if not app:
                raise serializers.ValidationError({'msg': '天使用户群组应指明app, 请输入appId'})
            if UserGroup.objects.filter(type__name=group_type.name, app=app).count() and self.get_method() == 'POST':
                raise serializers.ValidationError({'msg': '该app的天使用户群组已存在'})
            if not UserGroup.is_owner(self.current_user(), app):
                raise PermissionDenied('只有app管理员才能够创建/修改天使用户群组')

    def _validate_custom_group(self, app, group_type):
        if group_type.name == UserGroupType.CUSTOM and not UserGroup.is_owner(self.current_user(), app):
            raise PermissionDenied('只有app管理员才能够创建/修改自定义用户群组')

    def _validate_owner_group(self, app, group_type):
        if group_type.name == UserGroupType.OWNER:
            if not self.current_user().is_admin():
                raise PermissionDenied('只有平台管理员才能够创建/修改app管理员用户群组')
            if UserGroup.objects.filter(type__name=group_type.name, app=app).count() and self.get_method() == 'POST':
                raise serializers.ValidationError({'msg': '该app的管理员用户群组已存在'})

    class Meta:
        model = UserGroup
        fields = ('id', 'type', 'name', 'creator', 'appName', 'appId', 'memberCount', 'createdAt', 'updatedAt')
        validators = [
            UniqueTogetherValidator(
                queryset=UserGroup.objects.all(),
                fields=('app', 'name'),
                message='同一app下用户群组名称需唯一'
            )
        ]


class UserGroupMemberSerializer(AuthedSerializer):
    account = serializers.CharField(source='name')

    def create(self, validated_data):
        user_name = validated_data['name']
        user = None
        try:
            user = get_object_or_404(get_user_model(), username=user_name)
        except Http404:
            user = may_create_user_and_depts(user_name)

        if not user:
            raise serializers.ValidationError({'msg': '此用户不存在且无法创建'})
        group = self.context['view'].find_group()
        # one exception is user could let himself join angle group
        if not (group.type.name == UserGroupType.ANGEL and user == self.current_user()):
            self.context['view'].check_common_permission()
        if user in group.members.all():
            raise serializers.ValidationError({'msg': '此用户已经在群组中'})
        group.members.add(user)
        group.updated_time = datetime.datetime.now().time()
        return user

    @staticmethod
    def _get_angel_info(user):
        groups = UserGroup.objects.filter(type__name=UserGroupType.ANGEL, members__in=[user]).distinct()
        return [{"appId": group.app.id, "appName": group.app.name} for group in groups]

    def to_representation(self, value):
        result = {}
        group = self.context['view'].find_group()
        result['account'] = value.username
        result['id'] = value.id
        result['departmentLevel1'] = value.level_one_dep.name if value.level_one_dep else None
        result['departmentLevel2'] = value.level_two_dep.name if value.level_two_dep else None
        result['departments'] = [dep.name for dep in value.departments]
        result['phone'] = value.phone
        if group.app:
            result['appName'] = group.app.name
            result['appId'] = group.app.id
        else:
            result['appName'] = None
            result['appId'] = None
        result['angelForApps'] = self._get_angel_info(value)
        return result

    class Meta:
        model = get_user_model()
        fields = ('account',)


class DepartmentSerializer(serializers.ModelSerializer):
    parent = serializers.CharField(source='parent.name')

    class Meta:
        model = Department
        fields = ('name', 'parent', 'level')
