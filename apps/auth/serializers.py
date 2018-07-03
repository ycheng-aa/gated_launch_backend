from rest_framework import serializers
from apps.common.serializers import AuthedSerializer
from .models import User


class UserSerializer(AuthedSerializer):
    userName = serializers.CharField(source='username', required=False, read_only=True)
    chineseName = serializers.CharField(source='full_name', required=False, read_only=True)

    def to_representation(self, value):
        result = {}
        result['id'] = value.id
        result['userName'] = value.username
        result['chineseName'] = value.full_name
        result['departmentLevel1'] = value.level_one_dep.name if value.level_one_dep else None
        result['departmentLevel2'] = value.level_two_dep.name if value.level_two_dep else None
        result['phone'] = value.phone
        result['departments'] = [dep.name for dep in value.departments]
        return result

    class Meta:
        model = User
        fields = ('id', 'userName', 'chineseName', 'phone')
