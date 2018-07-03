from apps.common.routers import routers
from .views import GrayTasksViewSet, GrayStatusView, TaskExtendFieldView

routers.register(r'tasks', GrayTasksViewSet, 'tasks')
routers.register(r'taskStatus', GrayStatusView, 'status')
routers.register(r'tasks/(?P<task_id>\d+)/issueExtFields', TaskExtendFieldView, 'issueextfields')
