from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.common.gated_logger import gated_debug_logger
from apps.task_manager.models import GrayAppVersion
from apps.common.tasks import push_channels_task


@receiver(post_save, sender=GrayAppVersion, dispatch_uid="inner_strategy_push")
def send_push_channels(sender, instance, **kwargs):
    gated_debug_logger.debug("Receive Signals, Task:{}, step: {}".format(
        instance.gray_task_id,
        instance.current_step))
    if not kwargs.get('created'):
        gated_debug_logger.debug("Task:{}, step:{} is Update, Not need to send sms and mail".format(
            instance.gray_task_id,
            instance.current_step
        ))
        return None

    try:
        celery_id = push_channels_task(instance.gray_task_id, instance.current_step)
    except Exception as e:
        gated_debug_logger.error("Celery run fail. {}".format(e))
        return False
    gated_debug_logger.debug("Start pushing celery task successful, id: {}".format(celery_id))
    return True
