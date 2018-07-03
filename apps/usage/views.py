from rest_framework import mixins
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from apps.common.common_views import GetContextMixin
from apps.usage.models import EventTracking
from apps.usage.serializers import EventTrackingSerializer


class EventTrackingViewSet(mixins.CreateModelMixin, GenericViewSet, GetContextMixin):
    model = EventTracking
    queryset = EventTracking.objects.all()
    serializer_class = EventTrackingSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        """
        __Method__:
        POST

        __URL__: $LINK:eventtrackings-list$

        __Data__:

            {
                'type':                string,           # required
                'any_other_field':       string,         # optional, any other key-value string type pairs
            }

        __Response__:

            {
                "status": 200,
                "msg": "成功",
                "data": {
                    "type": "download",
                    "user": "app_owner_user",
                    "properties": [
                        {
                            "key": "any_other_key",
                            "value": "any_other_value"
                        }
                    ]
                }
            }
        """

        necessary_fields = set(['type'])
        data_keys = request.data.keys()
        # other key-value pairs should considered as properties
        property_keys = request.data.keys() - necessary_fields
        if necessary_fields - data_keys:
            raise ValidationError({'msg': "POST data must contain field(s): {}".format(', '.join(necessary_fields))})
        data = dict((k, request.data[k]) for k in necessary_fields)
        data['properties'] = [{'key': p, 'value': request.data[p]} for p in property_keys]
        data['user'] = request.user

        # basically CreateModelMixin implementation except the input data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
