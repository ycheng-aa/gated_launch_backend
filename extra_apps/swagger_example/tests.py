"""
Test to cover bulk create and update using serializers
"""

from __future__ import unicode_literals

from django.test import TestCase

from rest_framework import serializers


class BulkCreateSerializerTests(TestCase):
    """
    Creating mutiple instances using serializers
    """

    def setUp(self):
        class ExampleUserSerializer2(serializers.Serializer):
            id = serializers.IntegerField()
            username = serializers.CharField(max_length=50)
            email = serializers.EmailField()

        self.ExampleUserSerializer2 = ExampleUserSerializer2

    def test_bulk_create_success(self):
        """
        Correct bulk create serializer should return the input data.
        """

        data = [
            {
                'id': 0,
                'username': 'test_bulk_01',
                'email': 'test_bulk_01@qq.com'
            }, {
                'id': 1,
                'username': "test_bulk_02",
                'email': 'test_bulk_02@qq.com'

            }, {
                'id': 2,
                'username': 'test_bulk_03',
                'email': 'test_bulk_03@qq.com'
            }
        ]

        serializer = self.ExampleUserSerializer2(data=data, many=True)
        assert serializer.is_valid() is True
        assert serializer.validated_data == data
        assert serializer.errors == []
