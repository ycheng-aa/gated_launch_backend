from apps.common.routers import routers
from .views import UserGroupViewSet, UserGroupMemberViewSet, DepartmentViewSet

routers.register(r'userGroups', UserGroupViewSet, 'usergroups')
routers.register(r'userGroups/(?P<group_id>[^/]+)/members', UserGroupMemberViewSet, 'usergroupmems')
routers.register(r'departments', DepartmentViewSet, 'departments')
