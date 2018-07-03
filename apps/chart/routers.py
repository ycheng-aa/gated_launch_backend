from apps.common.routers import routers
from .views import UserChartViewSet, TaskChartViewSet, TaskChartDetailViewSet

routers.register(r'userChart', UserChartViewSet, 'userchart')
routers.register(r'taskChart', TaskChartViewSet, 'taskchart')
routers.register(r'taskChart/(?P<task_id>[^/]+)', TaskChartDetailViewSet, 'taskdetailchart')
