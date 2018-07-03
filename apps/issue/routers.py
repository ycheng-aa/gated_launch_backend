from apps.common.routers import routers
from .views import IssueViewSet, IssueStatusViewSet, IssueTypeViewSet, BusinessModuleViewSet,\
    PhoneBrandViewSet, RegionViewSet, IssueLiteViewSet

routers.register(r'issues', IssueViewSet, 'issues')
routers.register(r'issuesLite', IssueLiteViewSet, 'issueslite')
routers.register(r'issuestatus', IssueStatusViewSet, 'issuestatus')
routers.register(r'issuetypes', IssueTypeViewSet, 'issuetypes')
routers.register(r'businessModules', BusinessModuleViewSet, 'businessmodules')
routers.register(r'phoneBrands', PhoneBrandViewSet, 'phonebrands')
routers.register(r'regions', RegionViewSet, 'regions')
