import datetime
from django.contrib.auth import get_user_model
import requests
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from apps.common.gated_logger import gated_debug_logger
from apps.utils.utils import rtx_verify
from gated_launch_backend.settings import WEIXIN_API_URL, WEIXIN_APP_ID, WEIXIN_APP_SECRET
from .models import User
from .serializers import UserSerializer
from .filters import UserFilter
from rest_framework import permissions


class IsAppOrPlatOwner(permissions.BasePermission):
    """
        used for model User
        对于User来说，只有APP管理员或平台管理员能进行查询一些信息
    """

    def has_permission(self, request, view):
        result = False
        if request.user.is_admin() or request.user.is_owner():
            result = True
        return result


class UserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAppOrPlatOwner)
    filter_class = UserFilter


class ObtainExpiringAuthToken(ObtainAuthToken):

    # for security's sake, refresh every time get the post request,
    # let old one expire.
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = self._get_token(serializer.validated_data['user'])
            return Response({'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _get_token(in_user):
        token, created = Token.objects.get_or_create(user=in_user)
        token.created = datetime.datetime.utcnow()
        token.save()

        return token


class WeixinAuthToken(ObtainExpiringAuthToken):

    # accept {'jsCode': xxxx} or {'username': xxx, 'password': xxx, 'jsCode': xxxx}
    # The later one will connect weixin openid to ctx if all credential is correct.
    def post(self, request):
        if 'jsCode' not in request.data:
            return Response('No js code', status=status.HTTP_400_BAD_REQUEST)
        open_id = self._weixin_code_to_openid(request.data['jsCode'])
        if not open_id:
            return Response({'msg': 'Failed to login, Weixin code is wrong'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.filter(weixin_openid=open_id).first()
        # try to connect ctx and weixin account
        if not user and 'username' in request.data and 'password' in request.data and \
                rtx_verify(request.data['username'], request.data['password']):
            user = get_user_model().objects.filter(username=request.data['username']).first()
            if user is None:
                user = get_user_model().objects.create_user(username=request.data['username'],
                                                            password=request.data['password'])
            else:
                user.set_password(request.data['password'])
            user.weixin_openid = open_id
            user.save()
        if user:
            return Response(dict(token=self._get_token(user).key, **self._user_info(user)))
        return Response({'msg': 'Failed to login, can\'t recognize the Weinxin account and/or password is incorrect'},
                        status=status.HTTP_403_FORBIDDEN)

    @staticmethod
    def _user_info(user):
        return UserSerializer().to_representation(user)

    @staticmethod
    def _weixin_code_to_openid(js_code):
        result = False
        response = requests.get('{0}?appid={1}&secret={2}&js_code={3}&grant_type=authorization_code'.format(
            WEIXIN_API_URL, WEIXIN_APP_ID, WEIXIN_APP_SECRET, js_code,
        ))
        if response.status_code == status.HTTP_200_OK:
            if not response.json().get('openid'):
                gated_debug_logger.error('weixin get openid failed: ' + str(response.content))
            else:
                result = response.json().get('openid')
        return result


obtain_expiring_auth_token = ObtainExpiringAuthToken.as_view()

weixin_auth_token = WeixinAuthToken.as_view()
