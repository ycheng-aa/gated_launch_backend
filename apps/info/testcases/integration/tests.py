# -*- coding: utf-8 -*-
from rest_framework.test import APITestCase
from apps.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from apps.common.tests import GetResponseMixin


class InfoTestCase(APITestCase, GetResponseMixin):
    fixtures = [
        "apps/auth/fixtures/tests/info_api_test_users.json",
        "apps/user_group/fixtures/tests/info_api_test_user_groups.json",
        "apps/app/fixtures/tests/apps.json",
        "apps/common/fixtures/tests/images.json",
        "apps/app/fixtures/tests/app_types.json",
        "apps/task_manager/fixtures/tests/task_status.json",
        "apps/task_manager/fixtures/tests/info_api_test_graytask.json",
        "apps/task_manager/fixtures/tests/info_api_test_snapshotinnerstrategy.json",
        "apps/issue/fixtures/tests/info_api_test_issues.json",
        "apps/usage/fixtures/tests/usage_eventtype.json",
        "apps/usage/fixtures/tests/usage_property.json",
        "apps/usage/fixtures/tests/usage_eventtracking.json"
    ]

    def setUp(self):
        self.normal_user_new = User.objects.get(username='normal_user_new')
        self.normal_user_one_task = User.objects.get(username='normal_user_one_task')
        self.normal_user_two_task = User.objects.get(username='normal_user_two_task')
        self.admin_user = User.objects.get(username='admin_user')
        self.app_owner_user = User.objects.get(username='app_owner_user')
        self.user_one_task = User.objects.get(username='user_one_task')
        self.user_no_task = User.objects.get(username='user_no_task')

    def test_summary_user_not_in_no_app(self):
        self.client.force_authenticate(user=self.normal_user_new)
        url = reverse('mysummary')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['takenTasksCount'], 0)
        self.assertEqual(response.data['data']['reportedIssuesCount'], 0)
        self.assertEqual(response.data['data']['name'], 'normal_user_new')
        self.assertEqual(response.data['data']['awardCount'], 0)

    def test_summary_user_in_one_app(self):
        self.client.force_authenticate(user=self.normal_user_one_task)
        url = reverse('mysummary')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['takenTasksCount'], 1)

    def test_summary_user_in_two_app(self):
        self.client.force_authenticate(user=self.normal_user_two_task)
        url = reverse('mysummary')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['takenTasksCount'], 2)

    def test_task_user_in_innerstrategy(self):
        self.client.force_authenticate(user=self.user_one_task)
        url = reverse('mytasks-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['total'], 1)

    def test_user_no_task(self):
        self.client.force_authenticate(user=self.user_no_task)
        url = reverse('mytasks-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['total'], 0)

    def test_user_two_task(self):
        self.client.force_authenticate(user=self.normal_user_two_task)
        url = reverse('mytasks-list')
        data = {'page': 2, 'pageSize': 1}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['total'], 2)
        self.assertEqual(response.data['data']['results'][0]['taskName'], '0711飞凡灰度发布')

    def test_userCount_and_eventCount(self):
        self.client.force_authenticate(user=self.normal_user_two_task)
        url = reverse('takenstats')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['taskDetailEntry']['userCount'], 2)
        self.assertEqual(response.data['data']['taskDetailEntry']['eventCount'], 4)

    def test_userCount_and_eventCount_with_linkFrom(self):
        self.client.force_authenticate(user=self.normal_user_two_task)
        url = reverse('takenstats')
        data = {'linkFrom': 'poster'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['taskDetailEntry']['userCount'], 2)
        self.assertEqual(response.data['data']['taskDetailEntry']['eventCount'], 4)

    def test_userCount_and_eventCount_with_date(self):
        self.client.force_authenticate(user=self.normal_user_two_task)
        url = reverse('takenstats')
        data = {'startTime': '2017-09-19', 'endTime': '2017-09-21'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['taskDetailEntry']['userCount'], 2)
        self.assertEqual(response.data['data']['taskDetailEntry']['eventCount'], 3)

    def test_userCount_and_eventCount_with_appId_and_date(self):
        self.client.force_authenticate(user=self.normal_user_two_task)
        url = reverse('takenstats')
        data = {'appId': 1, 'startTime': '2017-09-19', 'endTime': '2017-09-21'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['taskDetailEntry']['userCount'], 2)
        self.assertEqual(response.data['data']['taskDetailEntry']['eventCount'], 2)

    def test_userCount_and_eventCount_with_appId_and_linkFrom(self):
        self.client.force_authenticate(user=self.normal_user_two_task)
        url = reverse('takenstats')
        data = {'appId': 1, 'linkFrom': 'poster'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['taskDetailEntry']['userCount'], 2)
        self.assertEqual(response.data['data']['taskDetailEntry']['eventCount'], 3)

    def test_userCount_and_eventCount_with_taskId_and_linkFrom_and_date(self):
        self.client.force_authenticate(user=self.normal_user_two_task)
        url = reverse('takenstats')
        data = {'taskId': 6, 'linkFrom': 'poster', 'startTime': '2017-09-19', 'endTime': '2017-09-21'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['taskDetailEntry']['userCount'], 1)
        self.assertEqual(response.data['data']['taskDetailEntry']['eventCount'], 1)

    def test_weixinloginstats_with_two_date(self):
        self.client.force_authenticate(user=self.normal_user_two_task)
        url = reverse('weixinloginstats')
        data = {'startTime': '2017-10-11', 'endTime': '2017-10-13'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['wxLoginEntry']), 3)

    def test_weixinloginstats_with_one_date(self):
        self.client.force_authenticate(user=self.normal_user_two_task)
        url = reverse('weixinloginstats')
        data = {'endTime': '2017-10-12'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['wxLoginEntry']), 2)
