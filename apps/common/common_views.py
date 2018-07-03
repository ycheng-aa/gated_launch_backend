from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class GetContextMixin(object):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class AuthedModelViewSet(viewsets.ModelViewSet, GetContextMixin):
    permission_classes = (IsAuthenticated,)
