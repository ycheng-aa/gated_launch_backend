# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-31 16:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0017_auto_20171026_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='kst_unread_flag',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AddField(
            model_name='issue',
            name='plat_unread_flag',
            field=models.NullBooleanField(default=False),
        ),
    ]
