from apps.common.routers import routers
from .views import InnerStrategyViewSet, OuterStrategyViewSet, StrategyViewSet

routers.register(r'strategies', StrategyViewSet, 'strategies')
routers.register(r'innerStrategies', InnerStrategyViewSet, 'innerStrategies')
routers.register(r'outerStrategies', OuterStrategyViewSet, 'outerStrategies')
