from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from apps.app.models import App
from apps.common.gated_logger import gated_debug_logger
from apps.issue.models import Issue, IssueExtValue
from apps.issue.views import IssueViewSet
from apps.user_group.models import UserGroup, UserGroupType
from apps.utils.utils import remove_model_object_from_cache, set_model_object_to_cache, clear_cache_with_prefix


@receiver([post_save, m2m_changed], sender=Issue)
def set_issue_obj_to_cache(sender, **kwargs):
    instance = kwargs.get('instance')
    if instance:
        try:
            if not kwargs.get('created'):
                set_model_object_to_cache(Issue, instance.pk, IssueViewSet.serializer_class(instance).data)
            # clear cache related to this creator
            clear_cache_with_prefix(instance.creator.username + ':')
        except Exception as e:
            gated_debug_logger.error(str(e))


@receiver([post_save, post_delete], sender=IssueExtValue)
def set_issue_obj_when_ext_values_changed(sender, **kwargs):
    instance = kwargs.get('instance')
    if instance:
        try:
            set_model_object_to_cache(Issue, instance.issue_id, IssueViewSet.serializer_class(instance.issue).data)
            # clear cache related to this creator
            clear_cache_with_prefix(instance.issue.creator.username + ':')
        except Exception as e:
            gated_debug_logger.error(str(e))


@receiver(post_delete, sender=Issue)
def remove_issue_obj_from_cache(sender, **kwargs):
    instance = kwargs.get('instance')
    if instance:
        try:
            remove_model_object_from_cache(Issue, instance.pk)
            # clear cache related to this creator
            clear_cache_with_prefix(instance.creator.username + ':')
        except Exception as e:
            gated_debug_logger.error(str(e))


@receiver(post_save, sender=App)
def create_app_angel(sender, **kwargs):
    if not kwargs.get('created'):
        return
    app = kwargs.get('instance')
    if app:
        for group_type in (UserGroupType.OWNER, UserGroupType.ANGEL, UserGroupType.ISSUE_HANDLER):
            if not UserGroup.objects.filter(type__name=group_type, app=app).exists():
                group = UserGroup.objects.create(type=UserGroupType.objects.get(name=group_type),
                                                 app=app,
                                                 name=app.name + '_' + group_type,
                                                 creator=app.creator)
                gated_debug_logger.debug("Created a new user group %s" % str(group))
