from django.contrib.auth import get_user_model
import time
from apps.common.gated_logger import gated_debug_logger
from apps.task_manager.models import GrayAppVersion, SnapshotInnerStrategy, GrayTask, GrayStatus, SnapshotOuterStrategy
from apps.common.utils import get_app_versions, send_email
from apps.user_group.models import UserGroup, UserGroupType
from apps.utils.utils import BpConfigOnline
from gated_launch_backend.settings import TURN_ON_STRATEGY_SMS_AND_EMAIL, SEND_EMAIL, BP_HOST


def strategy_push_content(task_id, step):
    gated_debug_logger.debug("Start strategy push by Signals, Task {}, steps : {}".format(task_id, step))
    instance = GrayAppVersion.objects.filter(gray_task_id=task_id, current_step=step)
    count = instance.count()
    if not instance:
        gated_debug_logger.error("Task {}, steps : {}".format(task_id, step))
        return None

    # 判断内部策略还是外部策略
    instance = instance.last()
    if instance.current_step <= instance.gray_task.inner_strategy_steps:
        gated_debug_logger.debug("Inner Strategys Push Start")
        gated_debug_logger.debug("Task: {}, step: {}; start Inner PUSH".format(
            instance.gray_task.id, instance.current_step))
        inner = SnapshotInnerStrategy.objects.filter(gray_task=instance.gray_task,
                                                     index=instance.current_step).first()

        if count > 1:
            gated_debug_logger.debug("Update version not need to send push")
            return None

        from apps.common.tasks import send_sms_task, send_email_task

        members = get_user_model().objects.filter(usergroup__in=inner.user_groups.all()).distinct().all()
        content = inner.push_content
        channels = [c.name for c in inner.push_channels.all()]
        phones = [m.phone for m in members]
        gated_debug_logger.debug("Send sms phone list : {}".format(phones))
        mails = [m.email for m in members]
        gated_debug_logger.debug("Send email list : {}".format(mails))
        if 'sms' in channels and TURN_ON_STRATEGY_SMS_AND_EMAIL:
            gated_debug_logger.debug("Task:{} Send SMS".format(inner.gray_task_id))
            celery_id = send_sms_task.delay(phones, content)
            gated_debug_logger.debug("Task:{} Send SMS celery id {}".format(inner.gray_task_id, celery_id))

        if 'mail' in channels and TURN_ON_STRATEGY_SMS_AND_EMAIL:
            gated_debug_logger.debug("Task:{} Send Mail".format(inner))
            # 发送的邮件标题为 task的名称
            celery_id = send_email_task.delay(mails, inner.gray_task.task_name, content)
            gated_debug_logger.debug("Task:{} Send Mail celery id {}".format(inner.gray_task_id, celery_id))

        gated_debug_logger.debug("Inner Strategys Push Complated")
    else:
        gated_debug_logger.debug("Task: {}, step: {}; start Outer PUSH".format(
            instance.gray_task.id, instance.current_step))
        outer_version = instance.android_version
        out_snap = SnapshotOuterStrategy.objects.filter(gray_task=instance.gray_task,
                                                        index=instance.current_step).first()
        # 外部策略版本发推送
        res = BpConfigOnline(out_snap.id, outer_version)
        if res["status"] != 200:
            gated_debug_logger.error("Outer Strategy Version Update Fail")
            gated_debug_logger.error(res)
        gated_debug_logger.debug("Strategy Push Completed")

    gated_debug_logger.debug("End strategy push by Signals")


def update_version_download():
    '''
    版本下载量实现如下：
    1、在页面的为策略每步的下载量的总和
    2、直接获取apphub的版本的下载量，不进行条件过滤
    3、版本下载量数据更新周期暂定： 5分钟，在celery定时任务中执行
    4、步骤结束后，停止更新此步骤指定的版本下载量
    5、如果步骤有更新了版本，则前一版本停止更新下载量，更新当前步骤的下载量
    6、如果任务结束，不再更新下载量
    '''

    task_list = GrayTask.objects.filter(current_status__name=GrayStatus.TESTING_STATUS).all()

    for task in task_list:
        version = task.grayappversion_set.all().last()
        if not version:
            gated_debug_logger.debug("Task: {}, not gray versions".format(task.id))
            continue
        elif version.current_step > task.inner_strategy_steps:
            gated_debug_logger.debug(
                "Task {}, step {} not need update download info; ".format(task.id, version.current_step))
            continue

        data = get_app_versions(download_urls=[version.ios_download_url, version.android_download_url])
        if not data.get("data"):
            gated_debug_logger.error(", ".join([
                "Task {}, step {} update version fail; ".format(task.id, version.current_step),
                "ios: {} ,android: {}".format(version.ios_version, version.android_version),
                "data : {}".format(data)
            ]))
            continue

        for s in data["data"]:
            if version.android_download_url == s["url_download"]:
                version.android_download_number = s["amount_of_download"]
            if version.ios_download_url == s["url_download"]:
                version.ios_download_number = s["amount_of_download"]
        version.save()
        gated_debug_logger.debug(", ".join([
            "Task {}, step {} update download successful; ".format(task.id, version.current_step),
            "ios {},{}".format(version.ios_version, version.ios_download_number),
            "android {},{}".format(version.android_version, version.android_download_number),
        ]))

    return True


def garytask_remind():
    if SEND_EMAIL:
        today = time.strftime("%F")
        tasks = GrayTask.objects.filter(end_date__lt=today, current_status__name=GrayStatus.TESTING_STATUS)
        for t in tasks:
            app_owner_members = UserGroup.objects.get(type__name=UserGroupType.OWNER, app=t.app).members
            emails = []
            for member in app_owner_members.all():
                emails.append(member.email)
            subject = "%s任务到期提醒" % t.task_name
            context = "亲爱的众测平台%s项目管理员，" \
                      "您负责项目的<<%s>>任务已于%s到期，" \
                      "请及时到众测平台关闭任务并处理用户反馈问题。\n" \
                      "地址：%s" % (t.app.name, t.task_name, t.end_date, BP_HOST)
            send_email(emails, subject=subject, context=context)
