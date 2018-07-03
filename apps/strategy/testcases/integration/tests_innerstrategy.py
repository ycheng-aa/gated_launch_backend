from rest_framework import status
from apps.common.tests import BaseTestCase
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from apps.common.tests import GetResponseMixin
from apps.auth.models import User
from apps.app.models import App


class StrategyRestTestCase(APITestCase, GetResponseMixin):
    fixtures = [
        "apps/common/fixtures/tests/images.json",
        "apps/app/fixtures/tests/app_types.json",
        "apps/app/fixtures/tests/apps.json",
        "apps/auth/fixtures/tests/departments.json",
        "apps/auth/fixtures/tests/users.json",
        "apps/user_group/fixtures/tests/user_groups.json",
    ]

    def setUp(self):
        self.app_owner_user = User.objects.get(username='app_owner_user')

    def test_get_innerstrategy_with_appId(self):
        self.client.force_authenticate(user=self.app_owner_user)
        response = self.client.get(reverse('innerStrategies-list'), {"appId": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('innerStrategies-list'), {"appId": "xxxx"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_outerstrategy_with_appId(self):
        self.client.force_authenticate(user=self.app_owner_user)
        response = self.client.get(reverse('outerStrategies-list'), {"appId": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('outerStrategies-list'), {"appId": "xxxx"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class InnerStrategyTestCase(BaseTestCase):
    '''
    内灰策略单元测试
    '''

    def setUp(self):
        self.normal_user = User.objects.get(username='normal_user')
        self.admin_user = User.objects.get(username='admin_user')

        # app1的app owner，对应测试过程中使用的app实例
        self.app1_owner_user = User.objects.get(username='app_owner_user')
        # app2的app owner
        self.app2_owner_user = User.objects.get(username='test_app_owner')

        # app1
        self.app = App.objects.get(pk=1)

        # 初始化Testcase所需参数
        # test_data：在测试过程中用于测试创建，删除，获取等接口时，临时插入内存数据库的测试数据
        # super_user：在测试获取和删除接口时，需要先插入测试数据（test_data）,super_user是一个有权限做此插入动作的用户
        # for_list_url, for_detail_url：testcase使用reverse方法逆向解析相关接口url，for_list_url,for_detail_url是接口url对应的名称
        self.test_data = {"name": "unit test innerstrategy",
                          "appId": 1,
                          "pushChannels": [1, 2],
                          "pushContent": "<p>this is some push content</p>",
                          "userGroups": []}
        self.super_user = self.app1_owner_user
        self.for_list_url = 'innerStrategies-list'
        self.for_detail_url = 'innerStrategies-detail'

    # get test cases

    def test_normal_user_can_not_get_innerstrategy(self):
        self.do_test_user_get_permission(self.normal_user, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_not_get_innerstrategy(self):
        self.do_test_user_get_permission(self.admin_user, status.HTTP_403_FORBIDDEN)

    def test_app_owner_user_can_get_innerstrategy(self):
        self.do_test_user_get_permission(self.app1_owner_user, status.HTTP_200_OK)

    def test_other_app_user_can_not_get_innerstrategy(self):
        self.do_test_user_get_permission(self.app2_owner_user, status.HTTP_403_FORBIDDEN)

    # patch test cases

    def test_normal_user_can_not_patch_innerstrategy(self):
        self.do_test_user_patch_permission(self.normal_user, {"name": "modified unit test innerstrategy"}, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_patch_innerstrategy(self):
        self.do_test_user_patch_permission(self.admin_user, {"name": "modified unit test innerstrategy"}, status.HTTP_403_FORBIDDEN)

    def test_app_owner_user_can_patch_innerstrategy(self):
        self.do_test_user_patch_permission(self.app1_owner_user, {"name": "modified unit test innerstrategy"}, status.HTTP_200_OK)

    def test_other_app_user_can_patch_innerstrategy(self):
        self.do_test_user_patch_permission(self.app2_owner_user, {"name": "modified unit test innerstrategy"}, status.HTTP_403_FORBIDDEN)

    # create test cases

    def test_normal_user_can_not_create_innerstrategy(self):
        self.do_test_user_create_permission(self.normal_user, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_not_create_innerstrategy(self):
        self.do_test_user_create_permission(self.admin_user, status.HTTP_403_FORBIDDEN)

    def test_app_owner_user_can_create_innerstrategy(self):
        self.do_test_user_create_permission(self.app1_owner_user, status.HTTP_200_OK)

    def test_other_app_owner_user_can_not_create_innerstrategy(self):
        self.do_test_user_create_permission(self.app2_owner_user, status.HTTP_403_FORBIDDEN)

    # delete test cases

    def test_normarl_user_can_not_delete_innerstrategy(self):
        self.do_test_user_delete_permission(user=self.normal_user,
                                            expect_status=status.HTTP_200_OK,
                                            extra_verify=lambda res: self.assertEqual(res.data.get('msg', {}), '1: You do not have permission to perform this action.'))

    def test_admin_user_can_not_delete_innerstrategy(self):
        self.do_test_user_delete_permission(user=self.admin_user,
                                            expect_status=status.HTTP_200_OK,
                                            extra_verify=lambda res: self.assertEqual(res.data.get('msg', {}), '1: You do not have permission to perform this action.'))

    def test_app_owner_user_can_delete_innerstrategy(self):
        self.do_test_user_delete_permission(user=self.app1_owner_user,
                                            expect_status=status.HTTP_200_OK,
                                            extra_verify=lambda res: self.assertEqual(res.data.get('msg', {}), u'成功'))

    def test_other_app_owner_user_can_not_delete_innerstrategy(self):
        self.do_test_user_delete_permission(user=self.app2_owner_user,
                                            expect_status=status.HTTP_200_OK,
                                            extra_verify=lambda res: self.assertEqual(res.data.get('msg', {}), '1: You do not have permission to perform this action.'))
