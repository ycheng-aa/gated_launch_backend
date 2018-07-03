import json
import mock
import os

from django.urls import reverse

from rest_framework.test import APITestCase

from django.conf import settings
from gated_launch_backend.settings_test import RTX_VERIFY_URL

_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')


# This method will be used by the mock to replace requests.post
def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.text = json.dumps(self.json_data)

    if kwargs['url'] == RTX_VERIFY_URL:
        return MockResponse({'status': 200}, 200)

    return MockResponse(None, 404)


class LoginTests(APITestCase):
    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_login(self, mock_post):
        with open(_FILE, encoding='utf-8') as file:
            test_data = json.load(file)

        url = reverse('Login')
        data = test_data.get("login", None)

        self.assertIsNotNone(data, msg="test_login: The test data file data is not consistent")

        debug = settings.DEBUG    # DEBUG 为 True 不生效, 若后续生效了删除此行
        settings.DEBUG = True     # DEBUG 为 True 不生效, 若后续生效了删除此行
        response = self.client.post(url, data, format='json')
        settings.DEBUG = debug    # DEBUG 为 True 不生效, 若后续生效了删除此行

        token = response.data['data'].get("token", None)

        self.assertIsNotNone(token, msg="test_login: Login Response is not correct")
