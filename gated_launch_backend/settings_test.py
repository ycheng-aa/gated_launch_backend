"""
Extra Django settings for test environment
"""

from .settings import *

# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

CELERY_BROKER_URL = ''
CELERY_RESULT_BACKEND = ''
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# skip external information query part
FFAN_STAFF_QUERY_URL = None

# 单测XML报告生成
TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
# 输出到XML和控制台
TEST_OUTPUT_VERBOSE = 2
TEST_OUTPUT_FILE_NAME = 'reports.xml'

# 单测中用到的url
RTX_VERIFY_URL = 'http://develop.ffan.com/rtx_verify'
JIRA_API_URL = 'http://10.213.45.106:10080/api/v1/CcJira/'
JIRA_ZC_USER = 'zhongce'

# 自动化测试中用到的url
ZHONGCE_SIT_URL="http://zhongce.sit.ffan.com/"
JIRA_SIT_URL = "http://10.213.45.106:10080/"

USE_CACHE = False
