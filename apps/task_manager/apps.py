from django.apps import AppConfig


class TaskManagementConfig(AppConfig):
    name = 'apps.task_manager'

    def ready(self):
        import apps.task_manager.signals  # noqa
