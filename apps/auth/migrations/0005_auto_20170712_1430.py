# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-12 14:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gated_launch_auth', '0004_user_phone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='role',
            new_name='_role',
        ),
    ]