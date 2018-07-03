from .models import ExampleUser
from rest_framework import serializers


class ExampleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleUser
        fields = ("id", "username", "email")


class ExampleBulkUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    email = serializers.EmailField()

    def create(self, validated_data):
        return ExampleUser.objects.create(**validated_data)


class BulkDeleteUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def destroy(self, validated_data):
        return
