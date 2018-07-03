from apps.common.routers import routers
from .views import UserViewSet

routers.register(r'users', UserViewSet, 'users')
