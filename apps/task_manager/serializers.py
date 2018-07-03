from rest_framework import serializers
from django.db import transaction
from django.shortcuts import get_object_or_404
from apps.common.serializers import AuthedSerializer
from .models import GrayTask, GrayStatus, SnapshotInnerStrategy, SnapshotOuterStrategy, IssueExtField
from apps.app.models import App
from apps.common.models import Image
from apps.common.utils import copy_model_to_model
from apps.strategy.models import InnerStrategy, OuterStrategy
from apps.common.gated_logger import gated_debug_logger


class GrayTasksSerializer(AuthedSerializer):
    startDate = serializers.DateField(source='start_date')
    endDate = serializers.DateField(source='end_date')
    appId = serializers.PrimaryKeyRelatedField(source='app', queryset=App.objects.all())
    imageId = serializers.PrimaryKeyRelatedField(source='image', queryset=Image.objects.all(), required=False)
    name = serializers.CharField(source="task_name")
    versionDesc = serializers.CharField(source="version_desc")
    awardRule = serializers.CharField(source="award_rule")
    contact = serializers.CharField(required=True)
    isJoinKesutong = serializers.BooleanField(source="is_join_kesutong", required=False)
    innerStrategyList = serializers.ListField(
        source="inner_strategy", required=False,
        child=serializers.DictField()
    )
    outerStrategyList = serializers.ListField(
        source="outer_strategy", required=False,
        child=serializers.IntegerField(min_value=1)
    )

    class Meta:
        model = GrayTask
        fields = ('id', 'appId', 'name', 'imageId', 'startDate', 'endDate', 'innerStrategyList', 'outerStrategyList',
                  'versionDesc', 'awardRule', 'contact', 'isJoinKesutong')

    def validate(self, data):
        validated_data = super().validate(data)
        task_name = validated_data.get("task_name")
        if not (self.instance and task_name == self.instance.task_name) and GrayTask.objects.filter(
                task_name=task_name).exists():
            msg = "The name is not allowed duplicate."
            gated_debug_logger.error(
                "Create Or Put Task Validate Data Fail, Error msg: {}; data: {}".format(msg, validated_data))
            raise serializers.ValidationError({"msg": "Create Or Put Task Validate Data Fail, {}".format(msg)})
        return validated_data

    def create(self, validated_data):
        inner_list = validated_data.get("inner_strategy", [])
        outer_list = validated_data.get("outer_strategy", [])
        validated_data['inner_strategy_steps'] = len(inner_list)
        validated_data['total_strategy_steps'] = len(inner_list) + len(outer_list)
        try:
            with transaction.atomic():
                instance = GrayTask(**validated_data)
                # 新建任务时候默认状态
                instance.current_status = GrayStatus.get_original_status()
                instance.creator = self.current_user()
                instance.save()

                index = 1
                for k in inner_list:
                    if not isinstance(k.get("id"), int):
                        raise serializers.ValidationError({"msg": "strategy id must be int"})
                    q = get_object_or_404(InnerStrategy, id=k.get("id"))
                    i = copy_model_to_model(
                        q,
                        SnapshotInnerStrategy,
                        pop_change_dict={'app_id': 'app', 'creator_id': 'creator'},
                        change_dict={'id': None, 'gray_task': instance, 'index': index},
                        data_change_dict={'user_groups': {}, 'push_channels': {}}
                    )
                    i.save()
                    i.user_groups = q.user_groups.all()
                    i.push_channels = q.push_channels.all()
                    if k.get("pushContent"):  # 更新推送内容
                        i.push_content = k.get("pushContent")
                    i.save()
                    index += 1
                for k in outer_list:
                    q = get_object_or_404(OuterStrategy, id=k)
                    i = copy_model_to_model(
                        q,
                        SnapshotOuterStrategy,
                        pop_change_dict={'app_id': 'app', 'creator_id': 'creator'},
                        change_dict={'id': None, 'gray_task': instance, 'index': index}
                    )
                    i.save()
                    index += 1
        except Exception as e:
            gated_debug_logger.error("Create Task Fail, Error msg: {}; data: {}".format(e, validated_data))
            raise serializers.ValidationError({"msg": "Create Task Fail, {}".format(e)})
        return instance

    def to_representation(self, task):
        return task.to_dict(detail=False)


class GrayStatusSerializer(AuthedSerializer):
    class Meta:
        model = GrayStatus
        fields = ('id', 'name', 'description')


class IssueExtFieldSerializer(AuthedSerializer):
    taskId = serializers.PrimaryKeyRelatedField(source='task', read_only=True)
    taskName = serializers.SlugRelatedField(source='task', slug_field='task_name', read_only=True)
    isOptional = serializers.BooleanField(source='is_optional', default=True)

    def create(self, validated_data):
        task = self.context['view'].find_task()
        validated_data['task'] = task

        if IssueExtField.objects.filter(task=task, name=validated_data['name']).first():
            raise serializers.ValidationError({'msg': '此任务已经有了同名扩展字段'})
        return super().create(validated_data)

    class Meta:
        model = IssueExtField
        fields = ('id', 'taskId', 'taskName', 'default', 'isOptional', 'type', 'name')
