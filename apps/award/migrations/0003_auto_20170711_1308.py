# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-11 13:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0003_merge_20170703_1410'),
        ('award', '0002_auto_20170629_1517'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='award',
            name='project_name',
        ),
        migrations.AddField(
            model_name='award',
            name='app',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.App'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='awardee',
            unique_together=set([('award', 'user')]),
        ),
    ]