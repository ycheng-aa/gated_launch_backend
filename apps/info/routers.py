from apps.common.routers import routers
from .views import MyTasksViewSet

routers.register(r'myTasks', MyTasksViewSet, 'mytasks')
