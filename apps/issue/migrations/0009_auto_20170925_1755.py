# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-25 17:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def update_issue_status(apps, schema_editor):
    status = apps.get_model('issue', 'IssueStatus')
    for k, v in (('验证', 'verifying'), ('挂起', 'suspending')):
        status.objects.get_or_create(name=k, description=v)


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0008_businessmodule_phonebrand_region'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssueReportSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True, verbose_name='问题报告来源名称')),
                ('desc', models.CharField(blank=True, max_length=100, null=True, verbose_name='问题报告来源描述')),
            ],
        ),
        migrations.AddField(
            model_name='issue',
            name='other',
            field=models.TextField(blank=True, null=True, verbose_name='附加信息，如小程序特定信息等'),
        ),
        migrations.AlterField(
            model_name='businessmodule',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='业务模块名称'),
        ),
        migrations.AlterField(
            model_name='issuestatus',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='状态名称'),
        ),
        migrations.AlterField(
            model_name='issuetype',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='分类名称'),
        ),
        migrations.AlterField(
            model_name='phonebrand',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='手机品牌'),
        ),
        migrations.AlterField(
            model_name='region',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='所属大区'),
        ),
        migrations.AddField(
            model_name='issue',
            name='report_source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='issue.IssueReportSource'),
        ),
        migrations.RunPython(update_issue_status),
    ]
