# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-13 16:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_merge_20170703_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='apphub_name',
            field=models.CharField(default=None, max_length=255, null=True, unique=True),
        ),
    ]