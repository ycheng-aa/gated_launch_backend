# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-10-13 11:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0011_auto_20171012_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='jira_link',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
