import json
from rest_framework import serializers
from apps.common.serializers import AuthedSerializer
from .models import InnerStrategy, OuterStrategy
from apps.app.models import App
from apps.user_group.models import UserGroup
from .models import PushChannel, Strategy


class InnerStrategySerializer(AuthedSerializer):
    createdAt = serializers.DateTimeField(source='created_time', required=False, read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_time', required=False, read_only=True)
    creator = serializers.CharField(source='creator.username', required=False)
    appId = serializers.PrimaryKeyRelatedField(source='app', queryset=App.objects.all())
    userGroups = serializers.PrimaryKeyRelatedField(source='user_groups', queryset=UserGroup.objects.all(), many=True)
    pushChannels = serializers.PrimaryKeyRelatedField(source='push_channels', queryset=PushChannel.objects.all(), many=True)
    pushContent = serializers.CharField(source='push_content', required=False)

    class Meta:
        model = InnerStrategy
        fields = ('id', 'name', 'appId', 'pushContent', 'creator',
                  'createdAt', 'updatedAt', 'userGroups', 'pushChannels')

    def create(self, validated_data):
        validated_data['creator'] = self.current_user()
        instance = super().create(validated_data)
        Strategy.objects.create(inner_strategy_id=instance.id, type="内部", creator_id=instance.creator_id, app_id=instance.app_id, name=instance.name)
        return instance


class OuterStrategySerializer(AuthedSerializer):
    createdAt = serializers.DateTimeField(source='created_time', required=False, read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_time', required=False, read_only=True)
    creator = serializers.CharField(source='creator.username', required=False)
    appId = serializers.PrimaryKeyRelatedField(source='app', queryset=App.objects.all())
    allowUsers = serializers.CharField(source='allow_users', required=False, allow_blank=True)
    rangeDates = serializers.CharField(source='range_dates', required=False, allow_blank=True)
    cityEnable = serializers.BooleanField(source='city_enable', required=False, default=True)
    cities = serializers.CharField(required=False, allow_blank=True)
    isCompatible = serializers.IntegerField(source='is_compatible', required=False)
    changeLog = serializers.CharField(source='change_log', required=False)
    changeLogImg = serializers.CharField(source='change_log_img', required=False)

    class Meta:
        model = OuterStrategy
        fields = ('id', 'name', 'appId', 'creator', 'createdAt', 'updatedAt', 'version', 'allowUsers',
                  'rangeDates', 'cities', 'cityEnable', 'channels', 'percentage', 'status',
                  'isCompatible', 'frequency', 'changeLog', 'changeLogImg')

    def create(self, validated_data):
        validated_data['creator'] = self.current_user()
        if validated_data.get('range_dates'):
            range_dates = None
            try:
                range_dates = json.loads(validated_data.get('range_dates'))
            except json.decoder.JSONDecodeError:
                raise serializers.ValidationError({"msg": "rangeDates is invalid format!"})

            if len(range_dates) > 0:
                for rd in range_dates:
                    if not (len(rd) == 3 and rd[0] != '' and rd[1] != '' and rd[2] != ''):
                        raise serializers.ValidationError({"msg": "rangeDates is invalid format! "
                                                                  "Example: [[\"2016-11-21 12:00\",\"2016-11-21 11:59\",\"3\"],[\"2016-11-21 12:00\",\"2016-11-21 11:59\",\"5\"]"})
        instance = super().create(validated_data)
        Strategy.objects.create(outer_strategy_id=instance.id, type="外部", creator_id=instance.creator_id, app_id=instance.app_id, name=instance.name)
        return instance


class StrategySerializer(AuthedSerializer):
    createdAt = serializers.DateTimeField(source='created_time', required=False, read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_time', required=False, read_only=True)
    creator = serializers.CharField(source='creator.username', required=False)
    innerStrategyId = serializers.PrimaryKeyRelatedField(source='inner_strategy', queryset=App.objects.all())
    outerStrategyId = serializers.PrimaryKeyRelatedField(source='outer_strategy', queryset=App.objects.all())

    class Meta:
        model = Strategy
        fields = ('id', 'name', 'creator', 'createdAt', 'updatedAt', 'type',
                  'innerStrategyId', 'outerStrategyId')
