# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-10-26 19:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0016_auto_20171023_2012'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ('-created_time', 'type'), 'verbose_name': 'issues'},
        ),
    ]
