# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from apps.common.utils import send_sms, send_email
from apps.common.utils import log_wrapper
from apps.utils.utils import sync_user_info_to_db, update_jira_to_zc, set_issues_to_cache, cache_app_owners, \
    auto_close_issue, delete_issues_from_statplat, check_issue_status_with_jira
from apps.task_manager.utils import strategy_push_content, update_version_download, garytask_remind


@shared_task
@log_wrapper
def sync_user_info():
    sync_user_info_to_db()


@shared_task
@log_wrapper
def send_sms_task(phones, message):
    send_sms(phones, message)


@shared_task
@log_wrapper
def send_email_task(emails, subject, content):
    send_email(emails, subject, content)


@shared_task
@log_wrapper
def push_channels_task(task_id, step):
    strategy_push_content(task_id, step)


@shared_task
@log_wrapper
def update_version_download_number():
    '''
    更新ios和android下载次数
    暂定 5 分钟更新一次
    :return:
    '''
    update_version_download()


@shared_task
@log_wrapper
def graytask_remind_task():
    """
    每天(12:00)遍历一遍task列表，到期还未关闭的任务，发邮件给该task所属项目的所有管理员，提醒他们关闭task
    :return:
    """
    garytask_remind()


@shared_task
@log_wrapper
def update_jira_to_zc_task():
    """
    定时查询jira变更，同步更新ZC issue
    """
    update_jira_to_zc()


@shared_task
@log_wrapper
def cache_issues_detailed_info():
    """
    将所有issue的详情加入缓存存储
    """
    set_issues_to_cache()


@shared_task
@log_wrapper
def cache_app_owners_task():
    """
    将app管理员的信息加入缓存
    """
    cache_app_owners()


@shared_task
@log_wrapper
def auto_close_issue_task():
    """
    每天(7:00)遍历一遍issue列表，对于未转jira的小程序问题，而且status是“验证”的，超过10天，自动关闭；同时添加一条comment：
    "AutoClosed: True.
    关闭原因：自动关闭。
    说 明：验证状态停留时间超过10天自动关闭。"
    关闭和添加comment所用账号均为相应issue的creator账号。
    :return:
    """
    auto_close_issue()


@shared_task
@log_wrapper
def delete_issues_from_statplat_task():
    """
    对于众测删除但是statplat还未对应的删除成功的issue追加删除
    """
    delete_issues_from_statplat()


@shared_task
@log_wrapper
def auto_check_issue_status_with_jira():
    """
    遍历issue列表，如果有issue的状态和对应jira的状态不一致的，发邮件通知负责人
    :return:
    """
    check_issue_status_with_jira()
