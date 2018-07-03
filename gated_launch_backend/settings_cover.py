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

# 单测中用到的url
RTX_VERIFY_URL = 'http://develop.ffan.com/rtx_verify'
JIRA_API_URL = 'http://10.213.45.106:10080/api/v1/CcJira/'
JIRA_ZC_USER = 'zhongce'

# 生成单测覆盖率报告
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=apps',
    '--cover-xml',
    '--cover-xml-file=coverage.xml',
]

USE_CACHE = False
