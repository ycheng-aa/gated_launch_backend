from rest_framework import status
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from apps.common.tests import BaseTestCase
from apps.auth.models import User
from apps.common.tests import GetResponseMixin


class AppRestTestCase(APITestCase, GetResponseMixin):
    fixtures = [
        "apps/common/fixtures/tests/images.json",
        "apps/app/fixtures/tests/app_types.json",
        "apps/app/fixtures/tests/apps.json",
        "apps/auth/fixtures/tests/departments.json",
        "apps/auth/fixtures/tests/users.json",
        "apps/user_group/fixtures/tests/user_groups.json",
    ]

    def setUp(self):
        self.normal_user = User.objects.get(username='normal_user')
        self.admin_user = User.objects.get(username='admin_user')
        self.app_owner_user = User.objects.get(username='app_owner_user')

    def test_admin_user_can_create_app_without_image_types(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('apps-list'),
                                    {"name": "unit test app",
                                     "desc": "unit test app",
                                     "component": 1,
                                     "status": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'unit test app')

    def test_get_with_str_pk(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('apps-detail', kwargs={'pk': "undefined"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AppTestCase(BaseTestCase):

    def setUp(self):
        self.normal_user = User.objects.get(username='normal_user')
        self.admin_user = User.objects.get(username='admin_user')

        self.test_data = {"name": "unit test app",
                          "desc": "unit test app",
                          "image": "aabbceadfdfdfdfdfdf",
                          "component": 1,
                          "status": 1,
                          "types": [1, 2, 3]
                          }
        self.super_user = self.admin_user
        self.for_list_url = 'apps-list'
        self.for_detail_url = 'apps-detail'

    # create test cases

    def test_normal_user_can_not_create_app(self):
        self.do_test_user_create_permission(self.normal_user, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_create_app(self):
        self.do_test_user_create_permission(self.admin_user, status.HTTP_200_OK)

    # get test cases

    def test_normal_user_can_get_app(self):
        self.do_test_user_get_permission(self.normal_user, status.HTTP_200_OK)

    def test_admin_user_can_get_app(self):
        self.do_test_user_get_permission(self.admin_user, status.HTTP_200_OK)

    # delete test cases
    def test_normal_user_can_not_delete_app(self):
        self.do_test_user_delete_item_permission(self.normal_user, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_delete_app(self):
        self.do_test_user_delete_permission(self.admin_user, status.HTTP_200_OK)

    # update test cases
    def test_normal_user_can_not_update_app(self):
        self.do_test_user_put_permission(self.normal_user, {'name': 'test modify app name'}, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_update_app(self):
        self.do_test_user_put_permission(self.admin_user, {'name': 'test modify app name'}, status.HTTP_200_OK)

    def test_admin_user_can_update_app_currentStatus(self):
        self.do_test_user_put_permission(self.admin_user, {'status': 2}, status.HTTP_200_OK)

    def test_admin_user_can_update_app_currentStatus_fail(self):
        self.do_test_user_put_permission(self.admin_user, {'status': 3}, status.HTTP_200_OK)
