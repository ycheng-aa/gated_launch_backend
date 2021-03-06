# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-31 09:25
from __future__ import unicode_literals

from django.db import migrations

def update_task_status(apps, update_data):
    status_arr = {'preparation': "未启动", 'testing': "进行中", 'finished': "已完成"}
    TaskStatus = apps.get_model('task_manager', 'graystatus')
    for k, v in status_arr.items():
        TaskStatus.objects.filter(name=k).update(description=v)

class Migration(migrations.Migration):

    dependencies = [
        ('task_manager', '0014_auto_20170829_1613'),
    ]

    operations = [
        migrations.RunPython(update_task_status)
    ]
