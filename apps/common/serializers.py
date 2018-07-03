from apps.app.models import App, AppType
from apps.auth.models import MAX_LENGTH
from apps.common.models import Image
from apps.user_group.models import UserGroup
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class AuthedSerializer(serializers.ModelSerializer):

    def current_user(self):
        return self.context['request'].user

    def get_method(self):
        return self.context['request'].method


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=1, max_length=MAX_LENGTH)
    password = serializers.CharField(min_length=1, max_length=128, style={'input_type': 'password'})
    id_code = serializers.CharField(min_length=4, max_length=5, required=False)


class AppVersionSerializer(serializers.Serializer):
    app_id_to_apphub_name = {}
    apphub_name_to_app_id_and_name = {}
    app_type_choices = []
    app = serializers.PrimaryKeyRelatedField(required=False, queryset=App.objects.all())
    app_type = serializers.ChoiceField(required=False, choices=app_type_choices)

    # 每次请求, 都要从数据库重新动态获取请求参数可选值
    @classmethod
    def reset_serializer(cls):
        query_set = App.objects.all().values('pk', 'name', 'apphub_name')
        cls.app_id_to_apphub_name = {str(item['pk']): item['apphub_name'] for item in query_set}
        cls.apphub_name_to_app_id_and_name = {
            item['apphub_name']: {'app_id': item['pk'], 'app_name': item['name']} for item in query_set
            if item['apphub_name'] is not None
        }
        cls.app_type_choices = (AppType.ANDROID, AppType.IOS)
        cls._declared_fields['app'] = serializers.PrimaryKeyRelatedField(required=False, queryset=App.objects.all())
        cls._declared_fields['app_type'] = serializers.ChoiceField(required=False, choices=cls.app_type_choices)

    def __init__(self, data):
        self.__class__.reset_serializer()
        super().__init__(data=data)


class SmsSerializer(serializers.Serializer):
    groups = serializers.PrimaryKeyRelatedField(many=True, queryset=UserGroup.objects.all())
    message = serializers.CharField(max_length=200)

    def validate(self, data):
        if len(data['groups']) == 0:
            raise Exception('groups should not be an empty list')
        return data


class EmailSerializer(serializers.Serializer):
    groups = serializers.PrimaryKeyRelatedField(many=True, queryset=UserGroup.objects.all())
    subject = serializers.CharField(max_length=255)
    context = serializers.CharField(max_length=7843)

    def validate(self, data):
        if len(data['groups']) == 0:
            raise serializers.ValidationError('groups should not be an empty list')
        return data


class UploadImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ('image_name', 'image_desc')
