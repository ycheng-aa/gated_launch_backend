from collections import OrderedDict
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.auth.models import User
from apps.common.tests import GetResponseMixin
from apps.usage.models import EventTracking


class UserGroupRESTTestCase(APITestCase, GetResponseMixin):
    fixtures = [
        "apps/auth/fixtures/tests/departments.json",
        "apps/auth/fixtures/tests/users.json",
    ]

    def setUp(self):
        self.normal_user = User.objects.get(username='normal_user')

    def test_create_event_log(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('eventtrackings-list')
        data = {'type': 'download', 'from': 'email', 'app': 'ffan', 'aaa': 'bbb'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)
        self.assertEqual(response.data,
                         OrderedDict([('status', 200), ('msg', '成功'),
                                      ('data', {'type': 'download', 'user': 'normal_user',
                                                'properties': [OrderedDict([('key', 'aaa'), ('value', 'bbb')]),
                                                               OrderedDict([('key', 'app'), ('value', 'ffan')]),
                                                               OrderedDict([('key', 'from'), ('value', 'email')])]})]))

        event_log = EventTracking.objects.get(user=self.normal_user)
        self.assertEqual(event_log.type.name, 'download')
        self.assertEqual(event_log.properties.count(), 3)
        self.assertEqual([(p.key, p.value) for p in event_log.properties.all().order_by('key')],
                         [('aaa', 'bbb'), ('app', 'ffan'), ('from', 'email')])

        # try again
        data = {'type': 'download', 'from': 'email', 'app': 'ffan', 'aaa': 'bbb'}
        self.client.post(url, data, format='json')

        self.assertEqual(EventTracking.objects.filter(user=self.normal_user).count(), 2)
        later_event_log = EventTracking.objects.filter(user=self.normal_user).order_by('-id').first()
        self.assertEqual([(p.key, p.value) for p in later_event_log.properties.all().order_by('key')],
                         [('aaa', 'bbb'), ('app', 'ffan'), ('from', 'email')])
