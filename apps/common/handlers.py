from django import db
from django.db.models.deletion import ProtectedError
from django.core import exceptions
from django.conf import settings
from rest_framework import views, status
from rest_framework.response import Response
import sys
import logging
from apps.utils.utils import may_log_exception_to_sentry


NOT_FOUND_JSON_RESPONSE = {'msg': 'Not found'}


def exception_handler(exc, context):
    """
    This handler will overwrite rest framework default handler, additionally,
    it will process ValidationError (most of them were raised by
    django.db.models and django.forms), DB error (Refs PEP249).

    Show some details about the error, if it's safe. It could be more useful
    when the server does not work well in production env.

    Setting the `exception` attribute on the response is not necessary as it
    will be done by REST Framework.
    """
    response = views.exception_handler(exc, context)

    # For development, we want to show the root cause stack in page.
    if settings.DEBUG:
        return response

    if response is None:
        if isinstance(exc, (exceptions.ValidationError, exceptions.FieldError)):
            # value is not correct or name is invalid.
            msg = exc.messages if hasattr(exc, 'messages') else str(exc)
            return Response({'msg': msg},
                            status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exc, exceptions.ObjectDoesNotExist):
            return Response({'msg': 'Not found:  %s' % str(exc)},
                            status=status.HTTP_404_NOT_FOUND)
        elif isinstance(exc, ProtectedError):
            return Response({"detail": "%s %s" % exc.args},
                            status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exc, ValueError):
            return Response({'msg': str(exc)},
                            status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exc, db.IntegrityError):
            # Refs PEP249
            # Maybe a duplicate PK, FK check fails, index conflict.
            return Response({'msg': str(exc)},
                            status=status.HTTP_409_CONFLICT)
        elif isinstance(exc, db.DatabaseError):
            # Refs PEP249
            # Other DB errors, such as incorrect grammar, transaction error etc.
            return Response({'msg': 'The database encountered an internal '
                                    'error or misconfiguration and was '
                                    'unable to complete your request.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger = logging.getLogger(__name__)
            logger.error('Unhandled exception', exc_info=sys.exc_info())
            may_log_exception_to_sentry()
            return Response(data=settings.INTERNAL_SERVER_ERROR_RESPONSE,
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return response
