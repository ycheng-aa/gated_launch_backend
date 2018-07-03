from apps.app.views import AppView
from apps.common.routers import routers

routers.register(r'apps', AppView, 'apps')
