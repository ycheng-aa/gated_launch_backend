# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-27 10:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrayAppVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('current_step', models.IntegerField(verbose_name='当前步骤')),
                ('version_name', models.CharField(max_length=256, verbose_name='版本名称')),
                ('version_number', models.CharField(max_length=256, verbose_name='版本号')),
                ('is_current_use', models.BooleanField(verbose_name='是否当前使用')),
                ('update_info', models.TextField(max_length=2000, verbose_name='任务更新信息')),
                ('expired', models.BooleanField(default=False, verbose_name='是否过期')),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.App', verbose_name='app')),
                ('app_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.AppType', verbose_name='android,ios, app类型')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GrayStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('status_id', models.IntegerField(verbose_name='状态')),
                ('status_name', models.CharField(max_length=256, verbose_name='状态名称')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GrayTaskLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('update_log', models.TextField(max_length=2000, verbose_name='更新字段名称和值')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GrayTaskRunStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('current_step', models.IntegerField(verbose_name='当前步骤')),
                ('update_info', models.TextField(max_length=2000, verbose_name='任务更新信息')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GrayTasks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('task_name', models.CharField(max_length=256, verbose_name='任务名称')),
                ('start_date', models.DateField(verbose_name='开始日期')),
                ('end_date', models.DateField(verbose_name='结束日期')),
                ('inner_strategy', models.CharField(max_length=256, verbose_name='内部策略id 列表')),
                ('outer_Strategy', models.CharField(max_length=256, verbose_name='外部测试id 列表')),
                ('created_date', models.DateField(verbose_name='创建日期')),
                ('current_step', models.IntegerField(verbose_name='当前步骤')),
                ('is_display', models.BooleanField(default=False, verbose_name='是否置顶')),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.App', verbose_name='app 外键')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户id')),
                ('current_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_manager.GrayStatus', verbose_name='灰度任务状态外键')),
                ('image_url', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='common.Image', verbose_name='图片地址')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InnerStrategy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('index', models.IntegerField(verbose_name='策略顺序')),
                ('Strategy', models.TextField(max_length=2000, verbose_name='策略详细信息')),
                ('gray_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_manager.GrayTasks', verbose_name='灰度任务id')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OuterStrategy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('index', models.IntegerField(verbose_name='策略顺序')),
                ('poster_url', models.CharField(max_length=256, verbose_name='策略图片地址')),
                ('Strategy', models.TextField(verbose_name='策略详细信息')),
                ('gray_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_manager.GrayTasks', verbose_name='灰度任务id')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='graytaskrunstatus',
            name='gray_task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_manager.GrayTasks', verbose_name='任务外键'),
        ),
        migrations.AddField(
            model_name='graytaskrunstatus',
            name='operator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户外键'),
        ),
        migrations.AddField(
            model_name='graytaskrunstatus',
            name='task_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_manager.GrayStatus', verbose_name='任务状态'),
        ),
        migrations.AddField(
            model_name='graytasklog',
            name='gray_task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_manager.GrayTasks'),
        ),
        migrations.AddField(
            model_name='graytasklog',
            name='operator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='操作人员'),
        ),
        migrations.AddField(
            model_name='grayappversion',
            name='current_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_manager.GrayStatus', verbose_name='任务状态'),
        ),
        migrations.AddField(
            model_name='grayappversion',
            name='gray_task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_manager.GrayTasks', verbose_name='任务外键'),
        ),
        migrations.AddField(
            model_name='grayappversion',
            name='inner_Strategy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_manager.InnerStrategy', verbose_name='内部策略'),
        ),
        migrations.AddField(
            model_name='grayappversion',
            name='operator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddField(
            model_name='grayappversion',
            name='outer_Strategy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_manager.OuterStrategy', verbose_name='外部策略'),
        ),
    ]
