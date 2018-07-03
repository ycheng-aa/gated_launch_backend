from collections import OrderedDict
import os
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.app.models import App
from apps.auth.models import User
from apps.award.models import Awardee
from apps.common.tests import GetResponseMixin


class AwardRESTTestCase(APITestCase, GetResponseMixin):
    fixtures = [
        "apps/common/fixtures/tests/images.json",
        "apps/app/fixtures/tests/app_types.json",
        "apps/app/fixtures/tests/apps.json",
        "apps/auth/fixtures/tests/departments.json",
        "apps/auth/fixtures/tests/users.json",
        "apps/user_group/fixtures/tests/user_groups.json",
        "apps/award/fixtures/tests/awards.json",
    ]

    def setUp(self):
        self.normal_user = User.objects.get(username='normal_user')
        self.admin_user = User.objects.get(username='admin_user')
        self.app_owner_user = User.objects.get(username='app_owner_user')
        self.app = App.objects.get(pk=1)
        self.file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'info.xlsx')

    def test_normal_user_could_not_import_awardees(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('importawardees-list', kwargs={'award_id': 1})

        with open(self.file_path, 'rb') as fp:
            response = self.client.post(url, data={'upload': fp})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_admin_user_could_not_import_awardees(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('importawardees-list', kwargs={'award_id': 1})

        with open(self.file_path, 'rb') as fp:
            response = self.client.post(url, data={'upload': fp})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_app_owner_could_import_awardees(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('importawardees-list', kwargs={'award_id': 1})

        with open(self.file_path, 'rb') as fp:
            response = self.client.post(url, data={'upload': fp})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_app_owner_import_awardees_response(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('importawardees-list', kwargs={'award_id': 1})

        with open(self.file_path, 'rb') as fp:
            response = self.client.post(url, data={'upload': fp})
        self.assertEqual(response.data, OrderedDict([('status', 200), ('msg', '成功'),
                                                     ('data',
                                                      {'fail': 1, 'totalCount': 5, 'success': 4,
                                                       'failed_detail': ['第5行 abcdefg: 奖励描述需要不为空并字数不超过10']
                                                       })]))

        with open(self.file_path, 'rb') as fp:
            response = self.client.post(url, data={'upload': fp})
        self.assertEqual(response.data, OrderedDict([('status', 200), ('msg', '成功'),
                                                     ('data',
                                                      {'totalCount': 5,
                                                       'failed_detail': ['第2行 normal_user: 对应用户已经被加入此次奖励',
                                                                         '第3行 admin_user: 对应用户已经被加入此次奖励',
                                                                         '第4行 22222222222222: 对应用户已经被加入此次奖励',
                                                                         '第5行 abcdefg: 奖励描述需要不为空并字数不超过10',
                                                                         '第6行 app_owner_user: 对应用户已经被加入此次奖励'],
                                                       'fail': 5, 'success': 0})]))

    def test_app_owner_import_awardees_effect(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('importawardees-list', kwargs={'award_id': 1})

        with open(self.file_path, 'rb') as fp:
            self.client.post(url, data={'upload': fp})

        self.assertTrue(Awardee.objects.filter(user__username='normal_user').exists())
        self.assertTrue(Awardee.objects.filter(user__username='admin_user').exists())
        self.assertTrue(Awardee.objects.filter(user__username='app_owner_user').exists())
        # this one only have phone info in excel file
        self.assertTrue(Awardee.objects.filter(user__username='manong').exists())

    def test_import_with_target_award_not_exist(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('importawardees-list', kwargs={'award_id': 10000000})

        with open(self.file_path, 'rb') as fp:
            response = self.client.post(url, data={'upload': fp})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, OrderedDict([('status', 400), ('msg', 'Not found.')]))
