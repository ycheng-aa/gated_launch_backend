# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-27 10:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20170731_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='apphub_name',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
