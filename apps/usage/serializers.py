from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from apps.common.fields import CreatableSlugField, ObjectSlugField
from apps.usage.models import EventType, EventTracking, Property


class PropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = ('key', 'value')


class EventTrackingSerializer(serializers.ModelSerializer):
    type = CreatableSlugField(slug_field='name', queryset=EventType.objects.all())
    user = ObjectSlugField(slug_field='username', queryset=get_user_model().objects.all())
    properties = PropertySerializer(many=True, required=False)

    class Meta:
        model = EventTracking
        fields = ('type', 'user', 'properties')

    def create(self, validated_data):
        with transaction.atomic():
            obj = self.Meta.model.objects.create(user=validated_data['user'], type=validated_data['type'])
            for prop in validated_data.get('properties', []):
                Property.objects.create(event=obj, **prop)

        return obj
