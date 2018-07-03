from apps.common.tasks import sync_user_info
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def force_sync_user_info(request):
    # Rest of the method
    s = sync_user_info.delay()
    return Response({'job id': s.id})
