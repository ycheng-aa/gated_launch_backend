from apps.auth.models import Role
from apps.common.serializers import EmailSerializer
from apps.common.tasks import send_email_task
from apps.user_group.models import UserGroup
from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView
from kombu.exceptions import OperationalError


# 接口文档
# http://wiki.ffan.biz/pages/viewpage.action?pageId=18514633#CommonApp接口文档-发送邮件
class EmailView(BenchmarkAPIView):
    '''
    发送邮件
    '''
    access = {'get': None, 'post': Role.APP_OWNER, 'put': None, 'delete': None}
    serializer_class = EmailSerializer

    def post_model(self, data=None):
        groups = self.data.get('groups')
        subject = self.data.get('subject')
        context = self.data.get('context')
        groups = UserGroup.objects.filter(pk__in=groups)
        emails = []
        for group in groups:
            members = group.members.all()
            for user in members:
                if user.email is not None and user.email not in emails:
                    emails.append(user.email)
        try:
            send_email_task.delay(emails, subject, context)
        except (ConnectionError, OperationalError):
            return self.get_response_by_code(1015)
        except Exception as e:
            return self.get_response_by_code(1, str(e))
        return self.get_response_by_code()
