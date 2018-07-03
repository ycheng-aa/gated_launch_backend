from collections import OrderedDict
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.app.models import App, AppComponent
from apps.auth.models import User, Role
from apps.user_group.models import UserGroupType, UserGroup
from apps.common.models import Image
from apps.common.tests import GetResponseMixin


class UserGroupRESTTestCase(APITestCase, GetResponseMixin):
    fixtures = [
        "apps/common/fixtures/tests/images.json",
        "apps/app/fixtures/tests/app_types.json",
        "apps/app/fixtures/tests/apps.json",
        "apps/app/fixtures/tests/app_components.json",
        "apps/auth/fixtures/tests/departments.json",
        "apps/auth/fixtures/tests/users.json",
        "apps/user_group/fixtures/tests/user_groups.json"
    ]

    def setUp(self):
        self.normal_user = User.objects.get(username='normal_user')
        self.admin_user = User.objects.get(username='admin_user')
        self.app_owner_user = User.objects.get(username='app_owner_user')
        self.app = App.objects.get(pk=1)

    def test_normal_user_could_not_create_company_group(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.COMPANY, 'name': 'company_group'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_normal_user_could_not_create_custom_group(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'custom_group', 'appId': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_normal_user_could_not_create_angel_group(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.ANGEL, 'name': 'group', 'appId': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_400_BAD_REQUEST)

    def test_judge_user_group_owner_correct(self):
        self.assertFalse(UserGroup.is_owner(self.normal_user, self.app))
        self.assertFalse(UserGroup.is_owner(self.admin_user, self.app))
        self.assertTrue(UserGroup.is_owner(self.app_owner_user, self.app))

    def test_could_not_create_multiple_angel_group(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')

        data = {'type': UserGroupType.ANGEL, 'name': 'group1', 'appId': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_400_BAD_REQUEST)

    def test_app_owner_could_not_create_app_owner_group(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.OWNER, 'name': 'group', 'appId': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_app_owner_could_create_multiple_custom_group(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'group', 'appId': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

        data = {'type': UserGroupType.CUSTOM, 'name': 'group1', 'appId': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_admin_could_create_company_group(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.COMPANY, 'name': 'company_group'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_admin_could_not_create_2_app_owner_group_for_1_app(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.OWNER, 'name': 'owner', 'appId': 2}
        self.client.post(url, data, format='json')

        data = {'type': UserGroupType.OWNER, 'name': 'owner_again', 'appId': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_app_owner_user_cannot_create_app_owner_group(self):
        url = reverse('usergroups-list')
        self.client.force_authenticate(user=self.app_owner_user)
        data = {'type': UserGroupType.OWNER, 'name': 'owner_again', 'appId': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_normal_user_cannot_create_app_owner_group(self):
        url = reverse('usergroups-list')
        self.client.force_authenticate(user=self.normal_user)
        data = {'type': UserGroupType.OWNER, 'name': 'owner_again', 'appId': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_normal_user_could_not_delete_app_user_group(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.ANGEL, 'appId': 1}
        response = self.client.get(url, data, format='json')
        group_id_1 = int(response.data.get('data').get('results')[0].get('id'))

        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'group2', 'appId': 1}
        response = self.client.post(url, data, format='json')
        group_id_2 = self._get_response_id(response)

        self.client.force_authenticate(user=self.normal_user)

        url = reverse('usergroups-detail', kwargs={'pk': group_id_1})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

        url = reverse('usergroups-detail', kwargs={'pk': group_id_2})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_app_owner_could_delete_app_user_group(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.ANGEL, 'appId': 1}
        response = self.client.get(url, data, format='json')
        group_id_1 = int(response.data.get('data').get('results')[0].get('id'))

        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'group2', 'appId': 1}
        response = self.client.post(url, data, format='json')
        group_id_2 = self._get_response_id(response)

        url = reverse('usergroups-detail', kwargs={'pk': group_id_1})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

        url = reverse('usergroups-detail', kwargs={'pk': group_id_2})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_company_user_group_could_not_be_deleted(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.COMPANY, 'name': 'company_group'}
        response = self.client.post(url, data, format='json')
        group_id = self._get_response_id(response)

        url = reverse('usergroups-detail', kwargs={'pk': group_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.normal_user)
        url = reverse('usergroups-detail', kwargs={'pk': group_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-detail', kwargs={'pk': group_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_normal_user_could_not_patch_user_group(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'group1', 'appId': 1}
        response = self.client.post(url, data, format='json')
        group_id = self._get_response_id(response)

        self.client.force_authenticate(user=self.normal_user)
        url = reverse('usergroups-detail', kwargs={'pk': group_id})
        response = self.client.patch(url, {'name': 'group2'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_app_owner_could_and_only_could_patch_app_user_group_name(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.ANGEL, 'appId': 1}
        response = self.client.get(url, data, format='json')
        group_id = int(response.data.get('data').get('results')[0].get('id'))

        url = reverse('usergroups-detail', kwargs={'pk': group_id})
        response = self.client.patch(url, {'name': 'group2'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

        url = reverse('usergroups-detail', kwargs={'pk': group_id})
        response = self.client.patch(url, {'name': 'group2', 'type': UserGroupType.CUSTOM}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_400_BAD_REQUEST)

    def _prepare_data_for_filter(self):
        # after the preparation, it should have 1 owner group (in fixtures),
        # 1 angel group, 1 company group, 2 custom group
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.ANGEL, 'name': 'angel_group', 'appId': 1}
        self.client.post(url, data, format='json')

        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'group1', 'appId': 1}
        self.client.post(url, data, format='json')

        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'group2', 'appId': 1}
        self.client.post(url, data, format='json')

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.COMPANY, 'name': 'company_group'}
        self.client.post(url, data, format='json')

    def test_filter_app_name(self):
        self._prepare_data_for_filter()
        response = self.client.get(reverse('usergroups-list'), {'appName': 'ffan'})
        self.assertEqual(self._get_response_total(response), 5)

        response = self.client.get(reverse('usergroups-list'), {'appName': 'aaabbb'})
        self.assertEqual(self._get_response_total(response), 0)

        response = self.client.get(reverse('usergroups-list'), {'appName': 'quick money'})
        self.assertEqual(self._get_response_total(response), 3)

        # create a quick money user group
        data = {'type': UserGroupType.OWNER, 'name': 'owner_group', 'appId': 2}
        self.client.post(reverse('usergroups-list'), data, format='json')

        response = self.client.get(reverse('usergroups-list'), {'appName': 'quick money'})
        self.assertEqual(self._get_response_total(response), 3)

    def test_filter_app_id(self):
        self._prepare_data_for_filter()
        response = self.client.get(reverse('usergroups-list'), {'appId': '1'})
        self.assertEqual(self._get_response_total(response), 5)

        response = self.client.get(reverse('usergroups-list'), {'appId': '32'})
        self.assertEqual(self._get_response_total(response), 0)

        # an automatically created group
        response = self.client.get(reverse('usergroups-list'), {'appId': '2'})
        self.assertEqual(self._get_response_total(response), 3)

    def test_filter_name(self):
        self._prepare_data_for_filter()
        response = self.client.get(reverse('usergroups-list'), {'name': 'group2'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(reverse('usergroups-list'), {'name': 'company_group'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(reverse('usergroups-list'), {'name': 'fake group'})
        self.assertEqual(self._get_response_total(response), 0)

    def test_filter_type(self):
        self._prepare_data_for_filter()
        response = self.client.get(reverse('usergroups-list'), {'type': 'owner'})
        self.assertEqual(self._get_response_total(response), 5)

        response = self.client.get(reverse('usergroups-list'), {'type': 'company'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(reverse('usergroups-list'), {'type': 'custom'})
        self.assertEqual(self._get_response_total(response), 2)

    def test_filter_parameters_combinations(self):
        self._prepare_data_for_filter()
        response = self.client.get(reverse('usergroups-list'), {'type': 'owner', 'appName': 'ffan'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(reverse('usergroups-list'), {'type': 'owner', 'appName': 'quick money'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(reverse('usergroups-list'), {'type': 'custom', 'appName': 'ffan'})
        self.assertEqual(self._get_response_total(response), 2)

        response = self.client.get(reverse('usergroups-list'), {'type': 'custom', 'appId': '1'})
        self.assertEqual(self._get_response_total(response), 2)

        response = self.client.get(reverse('usergroups-list'), {'type': 'custom', 'name': 'group1'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(reverse('usergroups-list'), {'type': 'custom', 'name': 'group1', 'appId': '1'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(reverse('usergroups-list'),
                                   {'type': 'custom', 'name': 'group1', 'appName': 'quick money'})
        self.assertEqual(self._get_response_total(response), 0)

        response = self.client.get(reverse('usergroups-list'), {'type': 'owner', 'name': 'group1'})
        self.assertEqual(self._get_response_total(response), 0)

        # create a quick money user group
        data = {'type': UserGroupType.OWNER, 'name': 'owner_group', 'appId': 2}
        self.client.post(reverse('usergroups-list'), data, format='json')

        response = self.client.get(reverse('usergroups-list'), {'type': 'owner', 'appName': 'quick money'})
        self.assertEqual(self._get_response_total(response), 1)

    def test_filter_name_with_vagueness_searching(self):
        self._prepare_data_for_filter()
        response = self.client.get(reverse('usergroups-list'), {'name': '1'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(reverse('usergroups-list'), {'name': 'oup1'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(reverse('usergroups-list'), {'name': 'group'})
        self.assertEqual(self._get_response_total(response), 3)

        response = self.client.get(reverse('usergroups-list'), {'name': 'angel'})
        self.assertEqual(self._get_response_total(response), 4)

    def test_post_response_format(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'group', 'appId': 1}
        response = self.client.post(url, data, format='json')
        self._remove_volatile_fields(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         OrderedDict([('status', 200), ('msg', '成功'),
                                      ('data', {'type': 'custom', 'memberCount': 0, 'appId': 1, 'appName': 'ffan',
                                                'name': 'group', 'creator': 'app_owner_user'})]))

    def test_get_detail_response_format(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'group', 'appId': 1}
        response = self.client.post(url, data, format='json')

        group_id = self._get_response_id(response)

        url = reverse('usergroups-detail', kwargs={'pk': group_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)
        self._remove_volatile_fields(response)
        self.assertEqual(response.data,
                         OrderedDict([('status', 200), ('msg', '成功'),
                                      ('data', {'type': 'custom', 'memberCount': 0, 'appId': 1, 'appName': 'ffan',
                                                'name': 'group', 'creator': 'app_owner_user'})]))

    def test_get_detail_not_found_response_format(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-detail', kwargs={'pk': 10000000000})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, OrderedDict([('status', 400), ('msg', 'Not found.')]))

    def test_get_not_login_response_format(self):
        url = reverse('usergroups-detail', kwargs={'pk': 1})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data,
                         OrderedDict([('status', 401), ('msg', 'Authentication credentials were not provided.')]))

    def test_get_delete_response_format(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'group', 'appId': 1}
        response = self.client.post(url, data, format='json')

        group_id = self._get_response_id(response)

        url = reverse('usergroups-detail', kwargs={'pk': group_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)
        self.assertEqual(response.data, OrderedDict([('status', 200), ('msg', '成功')]))

    def test_get_patch_response_format(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'group', 'appId': 1}
        response = self.client.post(url, data, format='json')

        group_id = self._get_response_id(response)

        url = reverse('usergroups-detail', kwargs={'pk': group_id})
        response = self.client.patch(url, format='json', data={'name': 'changed_name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)
        self._remove_volatile_fields(response)
        self.assertEqual(response.data, OrderedDict([('status', 200), ('msg', '成功'),
                                                     ('data', {'appName': 'ffan', 'creator': 'app_owner_user',
                                                               'type': 'custom', 'appId': 1, 'name': 'changed_name',
                                                               'memberCount': 0})]))

    def test_create_app_will_auto_create_its_owner_group_and_angel_group_and_handler_group(self):
        app = App.objects.create(name='aaa', image=Image.objects.all().first(),
                                 creator=User.objects.all().first(), component=AppComponent.objects.get(id=1))
        self.assertTrue(UserGroup.objects.filter(app=app,
                                                 type=UserGroupType.objects.get(name=UserGroupType.OWNER)).exists())
        owner_group = UserGroup.objects.get(app=app, type=UserGroupType.objects.get(name=UserGroupType.OWNER))
        self.assertEqual(owner_group.creator, app.creator)
        self.assertEqual(owner_group.name, 'aaa_owner')

        angel_group = UserGroup.objects.get(app=app, type=UserGroupType.objects.get(name=UserGroupType.ANGEL))
        self.assertEqual(angel_group.creator, app.creator)
        self.assertEqual(angel_group.name, 'aaa_angel')

        angel_group = UserGroup.objects.get(app=app, type=UserGroupType.objects.get(name=UserGroupType.ISSUE_HANDLER))
        self.assertEqual(angel_group.creator, app.creator)
        self.assertEqual(angel_group.name, 'aaa_issue_handler')

    def test_create_app_can_not_create_2_owner_group_and_angel_group_and_handler_group(self):
        app = App.objects.create(name='aaa', image=Image.objects.all().first(),
                                 creator=User.objects.all().first(), component=AppComponent.objects.get(id=1))
        with self.assertRaises(ValidationError) as e:
            UserGroup.objects.create(app=app,
                                     type=UserGroupType.objects.get(name=UserGroupType.OWNER),
                                     name='bbb')
        self.assertEqual(str(e.exception), "{'msg': ['One app should only have one owner group']}")

        with self.assertRaises(ValidationError) as e:
            UserGroup.objects.create(app=app,
                                     type=UserGroupType.objects.get(name=UserGroupType.ANGEL),
                                     name='ccc')
        self.assertEqual(str(e.exception), "{'msg': ['One app should only have one angel group']}")

        with self.assertRaises(ValidationError) as e:
            UserGroup.objects.create(app=app,
                                     type=UserGroupType.objects.get(name=UserGroupType.ISSUE_HANDLER),
                                     name='ccc')
        self.assertEqual(str(e.exception), "{'msg': ['One app should only have one issue_handler group']}")


class UserGroupMemberRESTTestCase(APITestCase, GetResponseMixin):
    fixtures = [
        "apps/common/fixtures/tests/images.json",
        "apps/app/fixtures/tests/app_types.json",
        "apps/app/fixtures/tests/apps.json",
        "apps/auth/fixtures/tests/departments.json",
        "apps/auth/fixtures/tests/users.json",
        "apps/user_group/fixtures/tests/user_groups.json"
    ]

    def setUp(self):
        self.normal_user = User.objects.get(username='normal_user')
        self.admin_user = User.objects.get(username='admin_user')
        self.app_owner_user = User.objects.get(username='app_owner_user')
        self.manong = User.objects.get(username='manong')
        self.manong_id = self.manong.id
        self.app = App.objects.get(pk=1)

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.COMPANY, 'name': 'company_group'}
        response = self.client.post(url, data, format='json')
        self.company_group_id = self._get_response_id(response)

        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.ANGEL, 'appId': 1}
        response = self.client.get(url, data, format='json')
        self.angel_group_id = int(response.data.get('data').get('results')[0].get('id'))

        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'group1', 'appId': 1}
        response = self.client.post(url, data, format='json')
        self.custom_group_id = self._get_response_id(response)

    def test_normal_user_could_not_add_member_to_owner_group(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': 1})
        data = {'account': 'manong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_normal_user_could_not_add_member_to_angel_group(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.angel_group_id})
        data = {'account': 'manong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_normal_user_could_not_add_member_to_custom_group(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.custom_group_id})
        data = {'account': 'manong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_owner_user_could_add_member_to_owner_group(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': 1})
        data = {'account': 'manong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_owner_user_could_add_member_to_handler_group(self):
        self.client.force_authenticate(user=self.app_owner_user)
        response = self.client.get(reverse('usergroups-list'), {'type': 'issue_handler', 'appId': '1'})
        group_id = response.data['data']['results'][0]['id']
        url = reverse('usergroupmems-list', kwargs={'group_id': group_id})
        data = {'account': 'manong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_owner_user_could_not_add_member_to_company_group(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = {'account': 'manong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_owner_user_could_add_member_to_angel_group(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.angel_group_id})
        data = {'account': 'manong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_owner_user_could_add_member_to_custom_group(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.custom_group_id})
        data = {'account': 'manong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_admin_user_could_add_member_to_owner_group(self):
        user_1 = get_user_model().objects.get(username='manong')
        self.assertIsNone(user_1.role)
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': 1})
        data = {'account': 'manong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)
        user_1.refresh_from_db()
        self.assertEqual(user_1.role, Role.app_owner_role)

    def test_normal_user_could_not_add_member_to_company_group(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = {'account': 'manong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_normal_user_could_not_read_group_members(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

        url = reverse('usergroupmems-list', kwargs={'group_id': self.custom_group_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

        url = reverse('usergroupmems-list', kwargs={'group_id': self.angel_group_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_admin_user_could_read_group_members(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

        url = reverse('usergroupmems-list', kwargs={'group_id': self.custom_group_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

        url = reverse('usergroupmems-list', kwargs={'group_id': self.angel_group_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_owner_user_could_read_company_and_his_group_members(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

        url = reverse('usergroupmems-list', kwargs={'group_id': self.custom_group_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

        url = reverse('usergroupmems-list', kwargs={'group_id': self.angel_group_id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_filter_account(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = {'account': 'manong'}
        response = self.client.get(url, data)
        self.assertEqual(self._get_response_total(response), 0)

        self.client.post(url, data, format='json')
        response = self.client.get(url, data)
        self.assertEqual(self._get_response_total(response), 1)

    def test_filter_department(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = {'departmentLevel1': '网科集团'}
        response = self.client.get(url, data)
        self.assertEqual(self._get_response_total(response), 0)

        response = self.client.post(url, {'account': 'manong'}, format='json')
        response = self.client.get(url, data)
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(url, {'departmentLevel2': '质量管理部'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(url, {'departmentLevel2': '质量管理部', 'departmentLevel1': '网科集团'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(url, {'departmentLevel2': '质量管理部', 'departmentLevel1': '网科集团',
                                         'account': 'manong'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(url, {'departmentLevel2': '质量管理部', 'departmentLevel1': '不存在部'})
        self.assertEqual(self._get_response_total(response), 0)

        response = self.client.get(url, {'departmentLevel1': '地产集团'})
        self.assertEqual(self._get_response_total(response), 0)

        response = self.client.get(url, {'departmentLevel2': '质量管理部', 'departmentLevel1': '网科集团',
                                         'account': 'mingong'})
        self.assertEqual(self._get_response_total(response), 0)

    def test_filter_direct_dep_is_l1_department(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = {'departmentLevel1': '网科集团'}
        response = self.client.get(url, data)
        self.assertEqual(self._get_response_total(response), 0)

        self.client.post(url, {'account': 'dalingdao'}, format='json')
        response = self.client.get(url, data)
        self.assertEqual(self._get_response_total(response), 1)

        # make sure the response data,
        # especially level 1 and level 2 department info
        self.assertEqual(response.data['data']['results'], [{'appName': None, 'appId': None,
                                                             'account': 'dalingdao', 'departmentLevel1': '网科集团',
                                                             'angelForApps': [], 'id': 6,
                                                             'phone': '33333333333333',
                                                             'departmentLevel2': None,
                                                             'departments': ['网科集团']}])

    def test_filter_phone(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = {'phone': '33333333333333'}
        response = self.client.get(url, data)
        self.assertEqual(self._get_response_total(response), 0)

        self.client.post(url, {'account': 'dalingdao'}, format='json')
        response = self.client.get(url, data)
        self.assertEqual(self._get_response_total(response), 1)

        # make sure the response data,
        # especially level 1 and level 2 department info
        self.assertEqual(response.data['data']['results'], [{'appName': None, 'appId': None,
                                                             'account': 'dalingdao', 'departmentLevel1': '网科集团',
                                                             'angelForApps': [], 'id': 6,
                                                             'phone': '33333333333333',
                                                             'departmentLevel2': None,
                                                             'departments': ['网科集团']
                                                             }])

    def test_filter_user_by_group_id(self):
        self.client.force_authenticate(user=self.admin_user)
        user_url = reverse('users-list')
        response = self.client.get(user_url, {'groupId': self.company_group_id})
        self.assertEqual(self._get_response_total(response), 0)

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = {'account': 'manong'}
        self.client.post(url, data, format='json')
        response = self.client.get(user_url, {'groupId': self.company_group_id})
        self.assertEqual(self._get_response_total(response), 1)

        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.angel_group_id})
        data = {'account': 'manong'}
        self.client.post(url, data, format='json')
        response = self.client.get(user_url, {'groupId': self.angel_group_id})
        self.assertEqual(self._get_response_total(response), 1)

        query_2_groups_url = user_url + "?groupId=%d&groupId=%d" % (self.company_group_id, self.angel_group_id)
        response = self.client.get(query_2_groups_url)
        # these 2 groups have same 1 member
        self.assertEqual(self._get_response_total(response), 1)

        # add another different member
        url = reverse('usergroupmems-list', kwargs={'group_id': self.angel_group_id})
        data = {'account': 'mingong'}
        self.client.post(url, data, format='json')
        response = self.client.get(query_2_groups_url)
        self.assertEqual(self._get_response_total(response), 2)

    def test_filter_user_by_with_account_name(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.angel_group_id})
        data = {'account': 'manong'}
        self.client.post(url, data, format='json')

        data = {'account': 'mingong'}
        self.client.post(url, data, format='json')

        url = reverse('usergroupmems-list', kwargs={'group_id': self.angel_group_id})

        query_url = url + "?account=mingong"
        response = self.client.get(query_url)
        self.assertEqual(self._get_response_total(response), 1)

        query_url = url + "?account=min"
        response = self.client.get(query_url)
        self.assertEqual(self._get_response_total(response), 1)

        query_url = url + "?account=no"
        response = self.client.get(query_url)
        self.assertEqual(self._get_response_total(response), 1)

        query_url = url + "?account=m"
        response = self.client.get(query_url)
        self.assertEqual(self._get_response_total(response), 2)

    def _prepare_data_for_delete(self):
        # add manong to company gorup, owner group, angel group,
        # and custome group
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = {'account': 'manong'}
        self.client.post(url, data, format='json')

        # owner group
        url = reverse('usergroupmems-list', kwargs={'group_id': 1})
        data = {'account': 'manong'}
        self.client.post(url, data, format='json')

        # angel group
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.angel_group_id})
        data = {'account': 'manong'}
        self.client.post(url, data, format='json')

        # custom group
        url = reverse('usergroupmems-list', kwargs={'group_id': self.custom_group_id})
        data = {'account': 'manong'}
        self.client.post(url, data, format='json')

    def test_normal_user_could_not_delete_member_in_any_group(self):
        self._prepare_data_for_delete()
        self.client.force_authenticate(user=self.normal_user)

        url = reverse('usergroupmems-detail', kwargs={'group_id': 1, 'pk': self.manong_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

        url = reverse('usergroupmems-detail', kwargs={'group_id': self.company_group_id, 'pk': self.manong_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

        url = reverse('usergroupmems-detail', kwargs={'group_id': self.angel_group_id, 'pk': self.manong_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

        url = reverse('usergroupmems-detail', kwargs={'group_id': self.custom_group_id, 'pk': self.manong_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_normal_user_could_add_himself_to_angel_group(self):
        self._prepare_data_for_delete()
        self.client.force_authenticate(user=self.normal_user)

        url = reverse('usergroupmems-list', kwargs={'group_id': self.angel_group_id})
        data = {'account': self.normal_user.username}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_owner_user_could_not_delete_member_in_company_group(self):
        self._prepare_data_for_delete()
        self.client.force_authenticate(user=self.app_owner_user)

        url = reverse('usergroupmems-detail', kwargs={'group_id': self.company_group_id, 'pk': self.manong_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_403_FORBIDDEN)

    def test_owner_user_could_delete_member_in_owner_group(self):
        self._prepare_data_for_delete()
        self.client.force_authenticate(user=self.app_owner_user)

        url = reverse('usergroupmems-detail', kwargs={'group_id': 1, 'pk': self.manong_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_owner_user_could_delete_member_in_custom_and_angel_group(self):
        self._prepare_data_for_delete()
        self.client.force_authenticate(user=self.app_owner_user)

        url = reverse('usergroupmems-detail', kwargs={'group_id': self.angel_group_id, 'pk': self.manong_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

        url = reverse('usergroupmems-detail', kwargs={'group_id': self.custom_group_id, 'pk': self.manong_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_admin_user_could_delete_member_in_company_and_owner_group(self):
        self._prepare_data_for_delete()
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('usergroupmems-detail', kwargs={'group_id': 1, 'pk': self.manong_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

        url = reverse('usergroupmems-detail', kwargs={'group_id': self.company_group_id, 'pk': self.manong_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

    def test_member_remove_from_owner_group_should_change_role(self):
        self._prepare_data_for_delete()
        self.client.force_authenticate(user=self.admin_user)
        self.manong.refresh_from_db()
        self.assertEqual(self.manong.role, Role.app_owner_role)

        url = reverse('usergroupmems-detail', kwargs={'group_id': 1, 'pk': self.manong_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_200_OK)

        # should change
        self.manong.refresh_from_db()
        self.assertIsNone(self.manong.role)

    def test_could_not_add_unrecognized_member_to_group(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.custom_group_id})
        data = {'account': 'unkonwn_person'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._get_business_status_code(response), status.HTTP_400_BAD_REQUEST)


class UserGroupMembersBulkOperationRESTTestCase(APITestCase, GetResponseMixin):
    fixtures = [
        "apps/common/fixtures/tests/images.json",
        "apps/app/fixtures/tests/app_types.json",
        "apps/app/fixtures/tests/apps.json",
        "apps/auth/fixtures/tests/departments.json",
        "apps/auth/fixtures/tests/users.json",
        "apps/user_group/fixtures/tests/user_groups.json"
    ]

    def setUp(self):
        self.normal_user = User.objects.get(username='normal_user')
        self.admin_user = User.objects.get(username='admin_user')
        self.app_owner_user = User.objects.get(username='app_owner_user')
        self.manong = User.objects.get(username='manong')
        self.manong_id = self.manong.id

        self.mingong = User.objects.get(username='mingong')
        self.mingong_id = self.mingong.id

        self.app = App.objects.get(pk=1)

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.COMPANY, 'name': 'company_group'}
        response = self.client.post(url, data, format='json')
        self.company_group_id = self._get_response_id(response)

        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroups-list')
        data = {'type': UserGroupType.ANGEL, 'appId': 1}
        response = self.client.get(url, data, format='json')
        self.angel_group_id = int(response.data.get('data').get('results')[0].get('id'))

        url = reverse('usergroups-list')
        data = {'type': UserGroupType.CUSTOM, 'name': 'group1', 'appId': 1}
        response = self.client.post(url, data, format='json')
        self.custom_group_id = self._get_response_id(response)

    def test_bulk_create(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = [{'account': 'manong'}, {'account': 'mingong'}]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrderedDict([('status', 200),
                                                     ('msg', '成功'),
                                                     ('data', {'failed': [],
                                                               'createdCount': 2,
                                                               'totalCount': 2})]))

        # create again
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data, OrderedDict([('status', 200),
                                                     ('msg', ['manong: 此用户已经在群组中', 'mingong: 此用户已经在群组中']),
                                                     ('data', {'totalCount': 2,
                                                               'failed': ['manong', 'mingong'],
                                                               'createdCount': 0})]))

    def test_bulk_delete(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = [{'account': 'manong'}, {'account': 'mingong'}]
        self.client.post(url, data, format='json')

        data = [self.manong_id, self.mingong_id]
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrderedDict([('status', 200),
                                                     ('msg', '成功'),
                                                     ('data', {'deletedCount': 2, 'failed': [],
                                                               'totalCount': 2})]))

        data = [self.manong_id, self.mingong_id]
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrderedDict([('status', 200),
                                                     ('msg', ['4: Not found.', '5: Not found.']),
                                                     ('data', {'deletedCount': 0,
                                                               'failed': data, 'totalCount': 2})]))

    def test_bulk_create_follow_permission_control(self):
        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = [{'account': 'manong'}, {'account': 'mingong'}]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrderedDict([('status', 200),
                                                     ('msg', ['manong: 只有平台管理员才能操作此用户',
                                                              'mingong: 只有平台管理员才能操作此用户']),
                                                     ('data', {'totalCount': 2, 'createdCount': 0,
                                                               'failed': ['manong', 'mingong']})]))

        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrderedDict([('status', 200),
                                                     ('msg', ['manong: 只有平台管理员才能操作此用户',
                                                              'mingong: 只有平台管理员才能操作此用户']),
                                                     ('data', {'totalCount': 2, 'createdCount': 0,
                                                               'failed': ['manong', 'mingong']})]))

    def test_bulk_delete_follow_permission_control(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = [{'account': 'manong'}, {'account': 'mingong'}]
        self.client.post(url, data, format='json')

        self.client.force_authenticate(user=self.app_owner_user)
        url = reverse('usergroupmems-list', kwargs={'group_id': self.company_group_id})
        data = [self.mingong_id, self.manong_id]
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrderedDict([('status', 200),
                                                     ('msg', ['5: 只有平台管理员才能操作此用户',
                                                              '4: 只有平台管理员才能操作此用户']),
                                                     ('data', {'deletedCount': 0, 'totalCount': 2,
                                                               'failed': data})]))

        self.client.force_authenticate(user=self.normal_user)
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrderedDict([('status', 200),
                                                     ('msg', ['5: 只有平台管理员才能操作此用户',
                                                              '4: 只有平台管理员才能操作此用户']),
                                                     ('data', {'deletedCount': 0, 'totalCount': 2,
                                                               'failed': data})]))


class DepartmentRESTTestCase(APITestCase, GetResponseMixin):
    fixtures = [
        "apps/auth/fixtures/tests/departments.json"
    ]

    def test_list_departments(self):
        response = self.client.get(reverse('departments-list'))
        self.assertEqual(self._get_response_total(response), 4)
        self.assertEqual(response.data, OrderedDict([('status', 200), ('msg', '成功'),
                                                     ('data', OrderedDict([('total', 4), ('next', None),
                                                                           ('previous', None),
                                                                           ('results',
                                                                            [OrderedDict([('name', '网科集团'),
                                                                                          ('parent', None),
                                                                                          ('level', 0)]),
                                                                             OrderedDict([('name', '质量管理部'),
                                                                                          ('parent', '网科集团'),
                                                                                          ('level', 1)]),
                                                                             OrderedDict([('name', '地产集团'),
                                                                                          ('parent', None),
                                                                                          ('level', 0)]),
                                                                             OrderedDict([('name', '工程部'),
                                                                                          ('parent', '地产集团'),
                                                                                          ('level', 1)])
                                                                             ])]))]))

    def test_filter_departments_by_parent(self):
        response = self.client.get(reverse('departments-list'), {'parent': '网科集团'})
        self.assertEqual(self._get_response_total(response), 1)
        self.assertEqual(response.data['data'], OrderedDict([('total', 1), ('next', None),
                                                             ('previous', None),
                                                             ('results',
                                                              [OrderedDict([('name', '质量管理部'),
                                                                            ('parent', '网科集团'),
                                                                            ('level', 1)])])]))

        response = self.client.get(reverse('departments-list'), {'parent': '找不到部门'})
        self.assertEqual(self._get_response_total(response), 0)

    def test_filter_departments_by_name(self):
        response = self.client.get(reverse('departments-list'), {'name': '网科集团'})
        self.assertEqual(self._get_response_total(response), 1)

        response = self.client.get(reverse('departments-list'), {'name': '找不到部门'})
        self.assertEqual(self._get_response_total(response), 0)

    def test_filter_departments_by_level(self):
        response = self.client.get(reverse('departments-list'), {'level': 0})
        self.assertEqual(self._get_response_total(response), 2)

        response = self.client.get(reverse('departments-list'), {'level': 1})
        self.assertEqual(self._get_response_total(response), 2)
