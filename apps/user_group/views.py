from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from apps.auth.models import Department
from apps.common.common_views import AuthedModelViewSet, GetContextMixin
from rest_framework import permissions
from rest_framework import mixins
from apps.user_group.filters import UserGroupFilter, UserGroupMemberFilter, DepartmentFilter
from .models import UserGroup, UserGroupType
from .serializers import UserGroupSerializer, UserGroupMemberSerializer, DepartmentSerializer


class IsAppOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        result = True
        if request.method in ('DELETE', 'PATCH', 'PUT') and \
                (obj.type.name in (UserGroupType.OWNER, UserGroupType.COMPANY) or
                 not UserGroup.is_owner(request.user, obj.app)):
                result = False
        return result


class UserGroupViewSet(AuthedModelViewSet):
    model = UserGroup
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupSerializer
    permission_classes = (IsAuthenticated, IsAppOwner)
    filter_class = UserGroupFilter


class NormalUserCanNotRead(permissions.BasePermission):

    def has_permission(self, request, view):
        result = True
        if request.user.is_admin():
            return result

        group = view.find_group()
        if request.method == 'GET':
            if group.is_company_group():
                result = request.user.is_owner()
            elif group.app:
                result = UserGroup.is_owner(request.user, group.app)

        return result


class UserGroupMemberViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin,
                             GenericViewSet,
                             GetContextMixin):
    model = get_user_model()
    queryset = get_user_model().objects.all().order_by('username')
    serializer_class = UserGroupMemberSerializer
    permission_classes = (IsAuthenticated, NormalUserCanNotRead)
    filter_class = UserGroupMemberFilter

    def find_group(self):
        return get_object_or_404(UserGroup, id=self.kwargs.get('group_id'))

    def get_queryset(self):
        return self.find_group().members.all()

    def check_common_permission(self):
        group = self.find_group()
        current_user = self.request.user
        if group.type.name == UserGroupType.COMPANY:
            if not current_user.is_admin():
                raise PermissionDenied('只有平台管理员才能操作此用户')
        elif group.type.name in (UserGroupType.ISSUE_HANDLER, UserGroupType.OWNER):
            if not current_user.is_admin() and not UserGroup.is_owner(current_user, group.app):
                raise PermissionDenied('只有app管理员或admin才能操作此用户')
        elif not UserGroup.is_owner(current_user, group.app):
            raise PermissionDenied('只有app管理员才能操作此用户')

    def perform_destroy(self, instance):
        self.check_common_permission()
        self.find_group().members.remove(instance)


class DepartmentViewSet(mixins.ListModelMixin, GenericViewSet):
    model = Department
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_class = DepartmentFilter
