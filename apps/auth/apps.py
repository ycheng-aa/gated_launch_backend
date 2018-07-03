from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = 'apps.auth'
    label = 'gated_launch_auth'
    verbose_name = 'Auth for gated launch'
