from apps.common.routers import routers
from apps.usage.views import EventTrackingViewSet

routers.register(r'eventTrackings', EventTrackingViewSet, 'eventtrackings')
