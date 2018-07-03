# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-10-23 20:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20170927_1054'),
        ('task_manager', '0017_auto_20170911_1855'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issue', '0015_auto_20171023_1248'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='issue',
            index_together=set([('app', 'task', 'creator')]),
        ),
    ]
