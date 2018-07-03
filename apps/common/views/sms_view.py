from apps.auth.models import Role
from apps.common.serializers import SmsSerializer
from apps.common.tasks import send_sms_task
from apps.user_group.models import UserGroup
from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView
from kombu.exceptions import OperationalError


# 接口文档
# http://wiki.ffan.biz/pages/viewpage.action?pageId=18514633#CommonApp接口文档-发送短信
class SmsView(BenchmarkAPIView):
    '''
    发送短信
    '''
    access = {'get': None, 'post': Role.APP_OWNER, 'put': None, 'delete': None}
    serializer_class = SmsSerializer

    def post_model(self, data=None):
        groups = self.data.get('groups')
        message = self.data.get('message')
        groups = UserGroup.objects.filter(pk__in=groups)
        phones = []
        for group in groups:
            members = group.members.all()
            for user in members:
                if user.phone is not None and len(user.phone) == 11 and user.phone not in phones:
                    phones.append(user.phone)
        try:
            send_sms_task.delay(phones, message)
        except (ConnectionError, OperationalError):
            return self.get_response_by_code(1015)
        except Exception as e:
            return self.get_response_by_code(1, str(e))
        return self.get_response_by_code()
