# from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from nose.tools import nottest
from apps.common.utils import get_response_business_status_code


class GetResponseMixin(object):
    def _get_business_status_code(self, response):
        return get_response_business_status_code(response)

    def _remove_volatile_fields(self, response):
        for key in ('createdAt', 'updatedAt', 'id'):
            if key in response.data.get('data', {}):
                response.data['data'].pop(key)

    def _get_response_total(self, response):
        return response.data.get('data', {}).get('total')

    def _get_response_id(self, response, key='id'):
        return response.data.get('data', {}).get(key)


class BaseTestCase(APITestCase, GetResponseMixin):

    def __init__(self, args):
        super().__init__(args)

        self.test_data = None
        self.super_user = None

        self.for_list_url = None
        self.for_detail_url = None

    fixtures = [
        "apps/app/fixtures/tests/apps.json",
        "apps/app/fixtures/tests/app_components.json",
        "apps/common/fixtures/tests/images.json",
        "apps/app/fixtures/tests/app_types.json",
        "apps/auth/fixtures/tests/users.json",
        "apps/auth/fixtures/tests/departments.json",
        "apps/strategy/fixtures/tests/strategy_data.json",
        "apps/user_group/fixtures/tests/user_groups.json",
        "apps/task_manager/fixtures/tests/task_data.json",
    ]

    @nottest
    def do_test(self, url, method, expect_status, authenticate=None, extra_verify=None, modify_data=None):
        res_id = None
        if authenticate is not None:
            self.client.force_authenticate(user=authenticate)

        if method.lower() == 'get':
            response = self.client.get(url)
        elif method.lower() == 'post':
            response = self.client.post(url, self.test_data, format='json')
            res_id = self._get_response_id(response)
        elif method.lower() == 'delete':
            response = self.client.delete(url, data=[1], format='json')
        elif method.lower() == 'patch':
            response = self.client.patch(url, data=modify_data, format='json')
        elif method.lower() == 'put':
            response = self.client.put(url, data=modify_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), expect_status)
        if extra_verify is not None:
            if callable(extra_verify):
                extra_verify(response)

        return res_id

    @nottest
    def do_test_user_get_permission(self, user, expect_status):
        res_id = self.do_test(url=reverse(self.for_list_url),
                              method='post',
                              expect_status=status.HTTP_200_OK,
                              authenticate=self.super_user)

        self.do_test(url=reverse(self.for_detail_url, kwargs={'pk': res_id}),
                     method='get',
                     expect_status=expect_status,
                     authenticate=user)

    @nottest
    def do_test_user_patch_permission(self, user, modify_data, expect_status):
        res_id = self.do_test(url=reverse(self.for_list_url),
                              method='post',
                              expect_status=status.HTTP_200_OK,
                              authenticate=self.super_user)

        self.do_test(url=reverse(self.for_detail_url, kwargs={'pk': res_id}),
                     method='patch',
                     expect_status=expect_status,
                     authenticate=user,
                     modify_data=modify_data)

    @nottest
    def do_test_user_put_permission(self, user, modify_data, expect_status):
        res_id = self.do_test(url=reverse(self.for_list_url),
                              method='post',
                              expect_status=status.HTTP_200_OK,
                              authenticate=self.super_user)

        self.do_test(url=reverse(self.for_detail_url, kwargs={'pk': res_id}),
                     method='put',
                     expect_status=expect_status,
                     authenticate=user,
                     modify_data=modify_data)

    @nottest
    def do_test_user_create_permission(self, user, expect_status):
        self.do_test(url=reverse(self.for_list_url),
                     method='post',
                     expect_status=expect_status,
                     authenticate=user)

    @nottest
    def do_test_user_delete_permission(self, user, expect_status, extra_verify=None):
        self.do_test(url=reverse(self.for_list_url),
                     method='post',
                     expect_status=status.HTTP_200_OK,
                     authenticate=self.super_user)

        self.do_test(url=reverse(self.for_list_url),
                     method='delete',
                     expect_status=expect_status,
                     authenticate=user,
                     extra_verify=extra_verify)

    @nottest
    def do_test_user_delete_item_permission(self, user, expect_status, extra_verify=None):
        res_id = self.do_test(url=reverse(self.for_list_url),
                              method='post',
                              expect_status=status.HTTP_200_OK,
                              authenticate=self.super_user)

        self.do_test(url=reverse(self.for_detail_url, kwargs={'pk': res_id}),
                     method='delete',
                     expect_status=expect_status,
                     authenticate=user,
                     extra_verify=extra_verify)
