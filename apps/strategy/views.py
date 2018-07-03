from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins
from rest_framework import permissions
from apps.user_group.models import UserGroup
from apps.app.models import App
from .models import InnerStrategy, OuterStrategy, Strategy
from .serializers import InnerStrategySerializer, OuterStrategySerializer, StrategySerializer
from .filters import InnerStrategyFilter, OuterStrategyFilter, StrategyFilter


class IsAppOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        result = False
        if request.method in ('DELETE', 'PATCH', 'PUT', 'GET'):
            result = UserGroup.is_owner(request.user, obj.app)
        return result

    def has_permission(self, request, view):
        result = True
        if request.method in ('POST', 'GET') and request.data.get('appId', None):
            app = get_object_or_404(App, id=request.data['appId'])
            result = UserGroup.is_owner(request.user, app)
        return result


class InnerStrategyViewSet(viewsets.ModelViewSet):
    model = InnerStrategy
    queryset = InnerStrategy.objects.all()
    serializer_class = InnerStrategySerializer
    permission_classes = (IsAuthenticated, IsAppOwner)
    filter_class = InnerStrategyFilter


class OuterStrategyViewSet(viewsets.ModelViewSet):
    model = OuterStrategy
    queryset = OuterStrategy.objects.all()
    serializer_class = OuterStrategySerializer
    permission_classes = (IsAuthenticated, IsAppOwner)
    filter_class = OuterStrategyFilter


class StrategyViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    model = Strategy
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = (IsAuthenticated,)
    filter_class = StrategyFilter
