from rest_framework.test import APITestCase
from apps.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status


class InfoTestCase(APITestCase):
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

    def test_taskChart_appDownload(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('taskchart-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['results'][0]['taskId'], 1)
        self.assertEqual(response.data['data']['results'][0]['appDownload'], 2)

    def test_taskChart_task_with_no_issue(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('taskdetailchart-list', kwargs={'task_id': 1})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # no issue about task 3
        url = reverse('taskdetailchart-list', kwargs={'task_id': 3})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
