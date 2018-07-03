import json
import os
import time
import requests

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from django.conf import settings

from extra_apps.wiremock_example.wiremock_utils import WiremockLocal

_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')


class LoginTests(APITestCase):
    def test_login(self):
        with open(_FILE, encoding='utf-8') as file:
            test_data = json.load(file)

        url = reverse('Login')
        data = test_data.get("login", None)

        self.assertIsNotNone(data, msg="test_login: The test data file data is not consistent")

        debug = settings.DEBUG  # DEBUG 为 True 不生效, 若后续生效了删除此行
        settings.DEBUG = True  # DEBUG 为 True 不生效, 若后续生效了删除此行
        response = self.client.post(url, data, format='json')
        settings.DEBUG = debug  # DEBUG 为 True 不生效, 若后续生效了删除此行
        token = response.data['data'].get("token", None)

        self.assertIsNotNone(token, msg="test_login: Login Response is not correct")


class LoginMockTests(APITestCase):
    def setUp(self):
        self.wiremock = WiremockLocal()
        self.wiremock.start()
        self.host = self.wiremock.base_url
        time.sleep(3)

        # Setup the Stub information for the API test
        login_data = {
            "request": {
                "url": "/rtx_verify",
                "method": "POST",
                "bodyPatterns": [
                    {"equalToJson": "{\"name\": \"tangyukun1\", \"password\": \"123456\"}",
                     "jsonCompareMode": "LENIENT"}
                ]
            },
            "response": {
                "status": 200,
                "jsonBody": {"status": 200, "message": "successfully"},
                "headers": {
                    "content-type": "application/json",
                    "x-token": "asdfasdfasdfasdfasdfasdfasdf"
                }
            }
        }

        self.wiremock.new(data=json.dumps(login_data))

    def tearDown(self):
        self.wiremock.stop()

    def test_login(self):
        url = self.host + "/rtx_verify"
        data = {"name": "tangyukun1", "password": "123456"}
        response = requests.post(url=url, data=json.dumps(data))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("message"), "successfully")
