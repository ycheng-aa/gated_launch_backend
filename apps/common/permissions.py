from rest_framework import permissions


class IsPlatformAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_admin()


class OnlyPlatformAdminCanRead(permissions.BasePermission):

    def has_permission(self, request, view):
        result = True
        if request.method == 'GET' and not request.user.is_admin():
            result = False
        return result


class OnlyAppOwnerCanRead(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        result = True
        if request.method == 'GET' and not self.is_app_owner_for_obj(request, view, obj):
            result = False
        return result

    # implement in subclass depend on it's specific context
    def is_app_owner_for_obj(self, request, view, obj):
        raise NotImplementedError
