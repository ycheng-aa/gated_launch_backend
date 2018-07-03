from apps.auth.views import ObtainExpiringAuthToken
from apps.common.serializers import LoginSerializer
from apps.user_group.models import UserGroupType
from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView, SETTINGS
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from rest_framework.exceptions import ValidationError
import base64
import json
import requests


class ObtainAuthTokenWithBase64(ObtainExpiringAuthToken):
    def auth(self, username, password):
        serializer = self.serializer_class(data={'username': username, 'password': password})
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return None, None
        user = serializer.validated_data['user']
        token = self._get_token(user)
        return token.key, user


# 接口文档
# http://wiki.ffan.biz/pages/viewpage.action?pageId=18514633#CommonApp接口文档-登录
class LoginView(BenchmarkAPIView):
    '''
    登录
    '''
    access = {'get': None, 'post': 'all', 'put': None, 'delete': None}
    serializer_class = LoginSerializer
    id_code_for_auto_test = 'bmapp'

    # 获取用户名密码, 可以使用同准入准出平台前端的 base64 加密方式, 也能不加密(方便后端调试)
    def get_username_password(self):
        auth_base64_tag = 'Basic '
        username = self.data['username']
        password = self.data['password']
        try:
            username = username.replace(auth_base64_tag, '')
            username = base64.b64decode(username).decode('ascii')
            password = password.replace(auth_base64_tag, '')
            password = base64.b64decode(password).decode('ascii')
            return username.strip(), password
        except Exception:
            return self.data['username'], self.data['password']

    # 验证万信用户名密码是否正确
    @classmethod
    def verify_ctx_account(cls, username, password):
        url = 'http://develop.ffan.com/rtx_verify'
        try:
            rsp = requests.post(url=url, data={'name': username, 'password': password})
            rsp = json.loads(rsp.text)
            if rsp['status'] == 200:
                return cls.get_response_by_code()
            else:
                return cls.get_response_by_code(1004)
        except:
            return cls.get_response_by_code(1009)

    def post_model(self, data=None):
        # 同 apphub 的验证码校验
        id_code = self.data.get('id_code', None)
        if 'valiation_code_image' in self.request.session.keys():
            session_id_code = self.request.session.get('valiation_code_image', None)
            self.request.session['valiation_code_image'] = None
        else:
            session_id_code = None
        # 自动化测试时候输入特定的验证码, 可以不用校验验证码
        if not settings.DEBUG or id_code != self.id_code_for_auto_test:
            if session_id_code is None or not isinstance(id_code, str) or id_code.lower() != session_id_code:
                return self.get_response_by_code(1005)
        auth = ObtainAuthTokenWithBase64()
        username, password = self.get_username_password()
        user_model = get_user_model()
        token, user = auth.auth(username, password)
        if token is None:
            res = self.verify_ctx_account(username, password)
            if res[SETTINGS.CODE] == SETTINGS.SUCCESS_CODE:
                user = user_model.objects.filter(username=username).first()
                if user is None:
                    user_model.objects.create_user(username=username, password=password)
                else:
                    user.set_password(password)
                    user.save()
                token, user = auth.auth(username, password)
                if token is None:
                    return self.get_response_by_code(1004)
            else:
                return res
        role_name = user.role
        if role_name is not None:
            role_name = role_name.name
        groups = user.usergroup_set.filter(type__name=UserGroupType.OWNER)
        apps = []
        inserted_apps = []
        for group in groups:
            if group.app is not None and group.app not in inserted_apps:
                inserted_apps.append(group.app)
                app = model_to_dict(group.app)
                app['types'] = [model_to_dict(type) for type in app['types']]
                apps.append(app)
        return self.get_response_by_code(data={'token': token, 'role': role_name, 'apps': apps})
