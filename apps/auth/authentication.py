import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = self.get_model().objects.get(key=key)
        except self.get_model().DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted')

        # compare time
        utc_now = datetime.datetime.utcnow()
        if utc_now > token.created + datetime.timedelta(seconds=settings.TOKEN_EXPIRATION_SECS):
            token.delete()
            raise AuthenticationFailed('Token has expired. Removed it from backend.')

        # treat the token as newly created
        token.created = utc_now
        token.save()
        return token.user, token
