from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gated_launch_backend.settings')

app = Celery('gated_launch_backend')

app.config_from_object('gated_launch_backend.settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
