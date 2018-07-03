from rest_framework import status
from apps.common.tests import BaseTestCase
from apps.auth.models import User
from apps.app.models import App


class OuterStrategyTestCase(BaseTestCase):
    '''
    外灰策略单元测试
    '''

    def setUp(self):
        self.normal_user = User.objects.get(username='normal_user')
        self.admin_user = User.objects.get(username='admin_user')

        # app1的app owner
        self.app1_owner_user = User.objects.get(username='app_owner_user')
        # app2的app owner
        self.app2_owner_user = User.objects.get(username='test_app_owner')

        # app1
        self.app = App.objects.get(pk=1)

        # 初始化Testcase所需参数
        self.test_data = {"name": "unit test outerstrategy",
                          "appId": 1,
                          "allowUsers": "4,5,6",
                          "isCompatible": 0,
                          "frequency": 2}
        self.super_user = self.app1_owner_user
        self.for_list_url = 'outerStrategies-list'
        self.for_detail_url = 'outerStrategies-detail'

    # get test cases

    def test_normal_user_can_not_get_outerstrategy(self):
        self.do_test_user_get_permission(self.normal_user, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_not_get_outerstrategy(self):
        self.do_test_user_get_permission(self.admin_user, status.HTTP_403_FORBIDDEN)

    def test_app_owner_user_can_get_outerstrategy(self):
        self.do_test_user_get_permission(self.app1_owner_user, status.HTTP_200_OK)

    def test_other_app_user_can_not_get_outerstrategy(self):
        self.do_test_user_get_permission(self.app2_owner_user, status.HTTP_403_FORBIDDEN)

    # patch test cases

    def test_normal_user_can_not_patch_outerstrategy(self):
        self.do_test_user_patch_permission(self.normal_user, {"name": "modified unit test outerstrategy"}, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_patch_outerstrategy(self):
        self.do_test_user_patch_permission(self.admin_user, {"name": "modified unit test outerstrategy"}, status.HTTP_403_FORBIDDEN)

    def test_app_owner_user_can_patch_outerstrategy(self):
        self.do_test_user_patch_permission(self.app1_owner_user, {"name": "modified unit test outerstrategy"}, status.HTTP_200_OK)

    def test_other_app_user_can_patch_outerstrategy(self):
        self.do_test_user_patch_permission(self.app2_owner_user, {"name": "modified unit test outerstrategy"}, status.HTTP_403_FORBIDDEN)

    # create test cases

    def test_normal_user_can_not_create_outerstrategy(self):
        self.do_test_user_create_permission(self.normal_user, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_not_create_outerstrategy(self):
        self.do_test_user_create_permission(self.admin_user, status.HTTP_403_FORBIDDEN)

    def test_app_owner_user_can_create_outerstrategy(self):
        self.do_test_user_create_permission(self.app1_owner_user, status.HTTP_200_OK)

    def test_other_app_owner_user_can_not_create_outerstrategy(self):
        self.do_test_user_create_permission(self.app2_owner_user, status.HTTP_403_FORBIDDEN)

    # delete test cases

    def test_normarl_user_can_not_delete_outerstrategy(self):
        self.do_test_user_delete_permission(user=self.normal_user,
                                            expect_status=status.HTTP_200_OK,
                                            extra_verify=lambda res: self.assertEqual(res.data.get('msg', {}), '1: You do not have permission to perform this action.'))

    def test_admin_user_can_not_delete_outerstrategy(self):
        self.do_test_user_delete_permission(user=self.admin_user,
                                            expect_status=status.HTTP_200_OK,
                                            extra_verify=lambda res: self.assertEqual(res.data.get('msg', {}), '1: You do not have permission to perform this action.'))

    def test_app_owner_user_can_delete_outerstrategy(self):
        self.do_test_user_delete_permission(user=self.app1_owner_user,
                                            expect_status=status.HTTP_200_OK,
                                            extra_verify=lambda res: self.assertEqual(res.data.get('msg', {}), u'成功'))

    def test_other_app_owner_user_can_not_delete_outerstrategy(self):
        self.do_test_user_delete_permission(user=self.app2_owner_user,
                                            expect_status=status.HTTP_200_OK,
                                            extra_verify=lambda res: self.assertEqual(res.data.get('msg', {}), '1: You do not have permission to perform this action.'))
