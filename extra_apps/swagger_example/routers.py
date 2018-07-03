from apps.common.routers import routers

from .views import ExampleUserViewSet1

routers.register(r'example_users', ExampleUserViewSet1, 'example_users')
