# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-26 15:09
from __future__ import unicode_literals

from django.db import migrations
from gated_launch_backend import settings


def remove_space_from_username(apps, schema_editor):
    label, model_name = settings.AUTH_USER_MODEL.split('.')
    for user in apps.get_model(label, model_name).objects.filter(username__contains=' '):
        user.username = user.username.strip()
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gated_launch_auth', '0007_user_weixin_openid'),
    ]

    operations = [
        migrations.RunPython(remove_space_from_username, reverse_code=migrations.RunPython.noop),
    ]
