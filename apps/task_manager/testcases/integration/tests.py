from collections import OrderedDict
from rest_framework import status
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from apps.common.tests import BaseTestCase, GetResponseMixin
from apps.app.models import App
from apps.auth.models import User


class GrayTasksTests(BaseTestCase):
    def setUp(self):
        self.normal_user = User.objects.get(username='normal_user')
        self.admin_user = User.objects.get(username='admin_user')
        self.app1_owner_user = User.objects.get(username='app_owner_user')
        self.app2_owner_user = User.objects.get(username='test_app_owner')
        self.app = App.objects.get(pk=1)

        self.test_data = {"name": "任务管理测试1",
                          "appId": 1,
                          "startDate": "2017-5-20",
                          "endDate": "2017-5-27",
                          "innerStrategyList": [{"id": 1, "pushContent": "innerStrategy1"},
                                                {"id": 1, "pushContent": "innerStrategy2"},
                                                {"id": 1, "pushContent": "innerStrategy3"},
                                                {"id": 1, "pushContent": "innerStrategy4"}],
                          "outerStrategyList": [1, 2],
                          "imageId": "aabbceadfdfdfdfdfdf",
                          "versionDesc": "11111111111111111111111",
                          "awardRule": "222222222222222222222",
                          "contact": "33333333333333333333333333"}
        self.super_user = self.app1_owner_user
        self.for_list_url = 'tasks-list'
        self.for_detail_url = 'tasks-detail'

    def test_normal_user_can_not_create_gray_task(self):
        # Todo: when the auth is enable, the expect_status code should be status.HTTP_403_FORBIDDEN
        self.do_test_user_create_permission(self.normal_user, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_create_gray_task(self):
        self.do_test_user_create_permission(self.admin_user, status.HTTP_403_FORBIDDEN)

    def test_app_owner_user_can_create_gray_task(self):
        self.do_test_user_create_permission(self.app1_owner_user, status.HTTP_200_OK)

    def test_other_app_owner_user_can_create_gray_task(self):
        self.do_test_user_create_permission(self.app2_owner_user, status.HTTP_403_FORBIDDEN)

    # delete test cases

    def test_normal_user_can_not_delete_gray_task(self):
        # Todo: when the auth is enable, the expect_status code should be status.HTTP_403_FORBIDDEN
        self.do_test_user_delete_permission(user=self.normal_user,
                                            expect_status=status.HTTP_200_OK,
                                            extra_verify=lambda res: self.assertEqual(res.data.get('msg', {}),
                                                                                      '1: You do not have permission to perform this action.'))

    def test_admin_user_can_delete_gray_task(self):
        self.do_test_user_delete_permission(user=self.admin_user,
                                            expect_status=status.HTTP_200_OK,
                                            extra_verify=lambda res: self.assertEqual(res.data.get('msg', {}),
                                                                                      '1: You do not have permission to perform this action.'))

    def test_app_owner_can_delete_gray_task(self):
        self.do_test_user_delete_permission(user=self.app1_owner_user,
                                            expect_status=status.HTTP_200_OK,
                                            extra_verify=lambda res: self.assertEqual(res.data.get('msg', {}), u'成功'))

    def test_other_app_owner_can_not_delete_gray_task(self):
        # Todo: when the auth is enable, the expect_status code should be status.HTTP_403_FORBIDDEN
        self.do_test_user_delete_permission(user=self.app2_owner_user,
                                            expect_status=status.HTTP_200_OK,
                                            extra_verify=lambda res: self.assertEqual(res.data.get('msg', {}),
                                                                                      '1: You do not have permission to perform this action.'))

    # get test cases

    def test_normal_user_can_get_task(self):
        # Todo: when the auth is enable, the expect_status code should be status.HTTP_200_OK
        self.do_test_user_get_permission(self.normal_user, status.HTTP_200_OK)


class GrayTasksDetailTests(APITestCase, GetResponseMixin):
    fixtures = [
        "apps/app/fixtures/tests/apps.json",
        "apps/common/fixtures/tests/images.json",
        "apps/app/fixtures/tests/app_types.json",
        "apps/auth/fixtures/tests/users.json",
        "apps/auth/fixtures/tests/departments.json",
        "apps/strategy/fixtures/tests/strategy_data.json",
        "apps/user_group/fixtures/tests/user_groups.json",
        "apps/task_manager/fixtures/tests/task_data.json",
        "apps/task_manager/fixtures/tests/info_api_test_graytask.json",

    ]

    def setUp(self):
        self.normal_user = User.objects.get(username='normal_user')
        self.admin_user = User.objects.get(username='admin_user')
        self.app1_owner_user = User.objects.get(username='app_owner_user')
        self.app2_owner_user = User.objects.get(username='test_app_owner')
        self.app = App.objects.get(pk=1)

        self.test_data = {"name": "任务管理测试2",
                          "appId": 1,
                          "startDate": "2017-5-20",
                          "endDate": "2017-5-27",
                          "innerStrategyList": [{"id": 1, "pushContent": "innerStrategy1"},
                                                {"id": 1, "pushContent": "innerStrategy2"},
                                                {"id": 1, "pushContent": "innerStrategy3"},
                                                {"id": 1, "pushContent": "innerStrategy4"}],
                          "outerStrategyList": [1, 2],
                          "imageId": "aabbceadfdfdfdfdfdf",
                          "versionDesc": "11111111111111111111111",
                          "awardRule": "222222222222222222222",
                          "contact": "33333333333333333333333333"}
        self.super_user = self.app1_owner_user
        self.for_list_url = 'tasks-list'
        self.for_detail_url = 'tasks-detail'
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url)
        response = self.client.post(url, self.test_data, format='json')
        self.task_id = self._get_response_id(response)

    def test_create_task_no_innerstrategylist(self):
        self.test_data["innerStrategyList"] = []
        self.test_data["name"] = "任务管理测试3"
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url)
        response = self.client.post(url, self.test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get("innerStrategyList"), None)

    def test_create_task_no_outerstrategylist(self):
        self.test_data["outerStrategyList"] = []
        self.test_data["name"] = "任务管理测试3"
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url)
        response = self.client.post(url, self.test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get("outerStrategyList"), None)

    def test_create_task_success_no_strategy(self):
        self.test_data["innerStrategyList"] = []
        self.test_data["outerStrategyList"] = []
        self.test_data["name"] = "任务管理测试3"
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url)
        response = self.client.post(url, self.test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get("name"), "任务管理测试3")

    def test_create_task_fail_by_inner_fail(self):
        self.test_data["innerStrategyList"] = [{"id": ""}]
        self.test_data["name"] = "任务管理测试3"
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url)
        response = self.client.post(url, self.test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("msg"), "Create Task Fail, {'msg': 'strategy id must be int'}")

    def test_create_task_no_permission(self):
        self.test_data["appId"] = 2
        self.test_data["name"] = "任务管理测试3"
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url)
        response = self.client.post(url, self.test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("msg"), "You do not have permission to perform this action.")

    def test_create_task_no_image(self):
        self.test_data.pop('imageId')
        self.test_data["name"] = "任务管理测试3"
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url)
        response = self.client.post(url, self.test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get("imageId"), "")

    def test_get_task_list(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url)
        self.test_data["name"] = "任务管理测试3"
        response = self.client.post(url, self.test_data, format='json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_response_total(response), 5)

    def test_get_task_list_is_join_kesutong(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(reverse('tasks-list'), {'isJoinKesutong': 'true'})
        self.assertEqual(self._get_response_total(response), 2)
        response = self.client.get(reverse('tasks-list'), {'isJoinKesutong': 'false'})
        self.assertEqual(self._get_response_total(response), 2)

    def test_get_task_list_isdisplay(self):
        url = reverse(self.for_list_url)
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(url + "?appId={}&isDisplay=true".format(self.app.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)
        self.assertEqual(self._get_response_total(response), 0)

        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/isDisplay/"
        is_display = {"isDisplay": "True"}
        response = self.client.patch(url, is_display, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('isDisplay'), True)

        url = reverse(self.for_list_url)
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(url + "?appId={}&isDisplay=true".format(self.app.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)
        self.assertEqual(self._get_response_total(response), 1)

    def test_get_task_by_id(self):
        url = reverse(self.for_detail_url, kwargs={'pk': self.task_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_response_id(response), self.task_id)

    def test_update_task_is_join_kesutong(self):
        url = reverse(self.for_detail_url, kwargs={'pk': self.task_id})
        response = self.client.patch(url, {"isJoinKesutong": "True"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['isJoinKesutong'], True)

        response = self.client.patch(url, {"isJoinKesutong": "False"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['isJoinKesutong'], False)

    def test_is_display_set_true(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url)
        self.test_data["name"] = "任务管理测试3"
        response = self.client.post(url, self.test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_response_id(response), 5)

        url = reverse(self.for_list_url) + str(self.task_id) + "/isDisplay/"
        is_display = {"isDisplay": "True"}
        response = self.client.patch(url, is_display, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('isDisplay'), True)

        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('isDisplay'), True)

    def test_is_display_set_false(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/isDisplay/"
        is_display = {"isDisplay": "false"}
        response = self.client.patch(url, is_display, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('isDisplay'), False)

    def test_is_display_fail_by_invalid_parameter(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/isDisplay/"
        is_display = {"isDisplay": "1"}
        response = self.client.patch(url, is_display, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('msg'), "isDisplay must be true or false")

    def test_start_test(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/startTest/"
        step = 1
        data = {
            "currentStep": step,
            "appVersion": {
                "android": {
                    "urlDownload": "http://apphub.ffan.com/api/appdownload/ffan/0/0/develop/4.20.0.0.1898//None/None/Feifan_o2o_4_20_0_0_DEV_1898_2017_08_01_release.apk",
                    "createDate": "2017-08-01",
                    "versionId": "4.20.0.0.1898"
                },
                "ios": {
                    "urlDownload": "http://apphub.ffan.com/api/appdownload/ffan/0/1/develop-Inhouse/4.20.0.1982//None/None/FeiFan-Inhouse.ipa",
                    "createDate": "2017-07-31",
                    "versionId": "4.20.0.1982"
                }
            }
        }

        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 2
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 2
        data['currentStep'] = step
        # 验证更新版本功能
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 3
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 4
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 5
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 6
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

    def test_start_test_with_no_version(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/startTest/"
        step = 1
        data = {
            "currentStep": step
        }

        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 2
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 2
        data['currentStep'] = step
        # 验证更新版本功能
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 3
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 4
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 5
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 6
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

    def test_start_test_fail(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/startTest/"
        step = 0
        data = {
            "currentStep": step,
            "appVersion": {
                "android": {
                    "urlDownload": "http://apphub.ffan.com/api/appdownload/ffan/0/0/develop/4.20.0.0.1898//None/None/Feifan_o2o_4_20_0_0_DEV_1898_2017_08_01_release.apk",
                    "createDate": "2017-08-01",
                    "versionId": "4.20.0.0.1898"
                },
                "ios": {
                    "urlDownload": "http://apphub.ffan.com/api/appdownload/ffan/0/1/develop-Inhouse/4.20.0.1982//None/None/FeiFan-Inhouse.ipa",
                    "createDate": "2017-07-31",
                    "versionId": "4.20.0.1982"
                }
            }
        }

        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 400)
        self.assertEqual(response.data.get('msg'), "current_step must be 1")

        step = 1
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 3
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 400)
        self.assertEqual(response.data.get('msg'), "current_step mast step by step or not large max")

        step = 5
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 400)
        self.assertEqual(response.data.get('msg'), "current_step mast step by step or not large max")

    def test_start_test_fail_with_no_version(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/startTest/"
        step = 0
        data = {
            "currentStep": step
        }

        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 400)
        self.assertEqual(response.data.get('msg'), "current_step must be 1")

        step = 1
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get('current_step'), step)

        step = 3
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 400)
        self.assertEqual(response.data.get('msg'), "current_step mast step by step or not large max")

        step = 5
        data['currentStep'] = step
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 400)
        self.assertEqual(response.data.get('msg'), "current_step mast step by step or not large max")

    def test_start_test_fail_no_auth(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/startTest/"
        step = 0
        data = {
            "currentStep": step,
            "appVersion": {
                "android": {
                    "urlDownload": "http://apphub.ffan.com/api/appdownload/ffan/0/0/develop/4.20.0.0.1898//None/None/Feifan_o2o_4_20_0_0_DEV_1898_2017_08_01_release.apk",
                    "createDate": "2017-08-01",
                    "versionId": "4.20.0.0.1898"
                },
                "ios": {
                    "urlDownload": "http://apphub.ffan.com/api/appdownload/ffan/0/1/develop-Inhouse/4.20.0.1982//None/None/FeiFan-Inhouse.ipa",
                    "createDate": "2017-07-31",
                    "versionId": "4.20.0.1982"
                }
            }
        }

        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_start_test_fail_status(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/currentStatus/"
        data = {
            "status": "finished",
        }

        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get("currentStatus"), "已结束")

        url = reverse(self.for_list_url) + str(self.task_id) + "/startTest/"
        step = 0
        data = {
            "currentStep": step,
            "appVersion": {
                "android": {
                    "urlDownload": "http://apphub.ffan.com/api/appdownload/ffan/0/0/develop/4.20.0.0.1898//None/None/Feifan_o2o_4_20_0_0_DEV_1898_2017_08_01_release.apk",
                    "createDate": "2017-08-01",
                    "versionId": "4.20.0.0.1898"
                },
                "ios": {
                    "urlDownload": "http://apphub.ffan.com/api/appdownload/ffan/0/1/develop-Inhouse/4.20.0.1982//None/None/FeiFan-Inhouse.ipa",
                    "createDate": "2017-07-31",
                    "versionId": "4.20.0.1982"
                }
            }
        }

        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 400)
        self.assertEqual(response.data.get('msg'), "Task was test completed!")

    def test_task_status(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/currentStatus/"
        data = {
            "status": "finished",
        }

        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get("currentStatus"), "已结束")

    def test_task_status_fail(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/currentStatus/"
        data = {
            "status": "finished",
        }

        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get("currentStatus"), "已结束")

        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('msg'), "Task can not be set to this status: finished")

    def test_update_image(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/image/"
        data = {
            "imageId": "eprghperahgioaergji",
        }

        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('data', {}).get("imageId"), "eprghperahgioaergji")

    def test_update_image_fail(self):
        self.client.force_authenticate(user=self.app1_owner_user)
        url = reverse(self.for_list_url) + str(self.task_id) + "/image/"
        data = {
            "imageId": "eprghperahgioaergji2",
        }

        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('msg'), "Update image  Fail, No Image matches the given query. ")


class TaskStatusTests(APITestCase, GetResponseMixin):
    fixtures = [
        "apps/app/fixtures/tests/apps.json",
        "apps/common/fixtures/tests/images.json",
        "apps/app/fixtures/tests/app_types.json",
        "apps/auth/fixtures/tests/users.json",
        "apps/auth/fixtures/tests/departments.json",
        "apps/strategy/fixtures/tests/strategy_data.json",
        "apps/user_group/fixtures/tests/user_groups.json",
        "apps/task_manager/fixtures/tests/task_data.json",
    ]

    def setUp(self):
        self.task_status_url = 'status-list'
        self.normal_user = User.objects.get(username='normal_user')

    def test_get_status(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse(self.task_status_url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_response_total(response), 3)


class TaskExtensionFieldTests(APITestCase, GetResponseMixin):
    fixtures = [
        "apps/app/fixtures/tests/apps.json",
        "apps/common/fixtures/tests/images.json",
        "apps/app/fixtures/tests/app_types.json",
        "apps/auth/fixtures/tests/users.json",
        "apps/auth/fixtures/tests/departments.json",
        "apps/strategy/fixtures/tests/strategy_data.json",
        "apps/user_group/fixtures/tests/user_groups.json",
        "apps/task_manager/fixtures/tests/task_data.json",
        "apps/task_manager/fixtures/tests/info_api_test_graytask.json"
    ]

    def setUp(self):
        self.client.force_authenticate(user=User.objects.get(username='app_owner_user'))

    def test_task_extension_field_create(self):
        url = reverse('issueextfields-list', kwargs={'task_id': 1})
        response = self.client.post(url, {'name': '广场'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrderedDict([('status', 200),
                                                     ('msg', '成功'),
                                                     ('data', {'id': 1, 'isOptional': True, 'name': '广场',
                                                               'type': None, 'taskId': 1,
                                                               'default': None, 'taskName': '0711飞凡灰度发布'})]))

        response = self.client.post(url, {'name': '手机型号', 'isOptional': True, 'default': 'iPhone', 'type': 'string'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         OrderedDict([('status', 200), ('msg', '成功'),
                                      ('data', {'id': 2, 'isOptional': True, 'name': '手机型号',
                                                'type': 'string', 'taskId': 1, 'default': 'iPhone',
                                                'taskName': '0711飞凡灰度发布'})]))

    def test_task_extension_field_can_not_create_same_name_twice(self):
        url = reverse('issueextfields-list', kwargs={'task_id': 1})
        self.client.post(url, {'name': '手机型号'})
        response = self.client.post(url, {'name': '手机型号'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrderedDict([('status', 400), ('msg', '此任务已经有了同名扩展字段')]))

    def test_task_extension_field_patch(self):
        url = reverse('issueextfields-list', kwargs={'task_id': 1})
        self.client.post(url, {'name': '广场'})

        response = self.client.patch(reverse('issueextfields-detail',
                                             kwargs={'task_id': 1, 'pk': 1}), {'name': '所在万达广场'})
        self.assertEqual(response.data, OrderedDict([('status', 200),
                                                     ('msg', '成功'),
                                                     ('data', {'id': 1, 'isOptional': True, 'name': '所在万达广场',
                                                               'type': None, 'taskId': 1,
                                                               'default': None, 'taskName': '0711飞凡灰度发布'})]))

    def test_task_extension_field_get_detail(self):
        url = reverse('issueextfields-list', kwargs={'task_id': 1})
        self.client.post(url, {'name': '广场'})

        response = self.client.get(reverse('issueextfields-detail', kwargs={'task_id': 1, 'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         OrderedDict([('status', 200), ('msg', '成功'),
                                      ('data', {'isOptional': True, 'taskName': '0711飞凡灰度发布',
                                                'type': None, 'id': 1, 'default': None, 'name': '广场', 'taskId': 1})]))

    def test_task_extension_field_delete(self):
        url = reverse('issueextfields-list', kwargs={'task_id': 1})
        self.client.post(url, {'name': '广场'})

        response = self.client.delete(reverse('issueextfields-detail', kwargs={'task_id': 1, 'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrderedDict([('status', 200), ('msg', '成功')]))

        # confirm it's really deleted
        response = self.client.get(reverse('issueextfields-list', kwargs={'task_id': 1}))
        self.assertEqual(response.data,
                         OrderedDict([('status', 200), ('msg', '成功'),
                                      ('data', OrderedDict([('total', 0), ('next', None),
                                                            ('previous', None), ('results', [])]))]))

    def test_task_extension_field_list_and_filter(self):
        url = reverse('issueextfields-list', kwargs={'task_id': 1})
        self.client.post(url, {'name': '广场'})
        self.client.post(url, {'name': '手机型号', 'isOptional': True, 'default': 'iPhone', 'type': 'string'})

        response = self.client.get(url)
        self.assertEqual(self._get_response_total(response), 2)

        response = self.client.get(url, {'name': '广场'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(url, {'name': '手机型号'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(url, {'name': '汪汪'})
        self.assertEqual(self._get_response_total(response), 0)

        response = self.client.get(url, {'isOptional': True})
        self.assertEqual(self._get_response_total(response), 2)

        response = self.client.get(url, {'isOptional': False})
        self.assertEqual(self._get_response_total(response), 0)

        response = self.client.get(url, {'type': 'string'})
        self.assertEqual(self._get_response_total(response), 1)

        # 联合查询
        response = self.client.get(url, {'name': '手机型号', 'isOptional': True, 'type': 'string'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(url, {'name': '广场', 'isOptional': True, 'type': 'string'})
        self.assertEqual(self._get_response_total(response), 0)

        response = self.client.get(url, {'name': '广场', 'isOptional': True})
        self.assertEqual(self._get_response_total(response), 1)
