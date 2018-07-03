from apps.common.routers import routers
from .views import ImportAwardeesView


routers.register(r'award/(?P<award_id>[^/]+)/import-awardees', ImportAwardeesView, base_name='importawardees')
