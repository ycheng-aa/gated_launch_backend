from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import SET_NULL

from apps.common.models import CommonInfoModel
from apps.app.models import App


class UserGroupType(CommonInfoModel):
    # define constant
    ANGEL = 'angel'
    COMPANY = 'company'
    CUSTOM = 'custom'
    OWNER = 'owner'
    ISSUE_HANDLER = 'issue_handler'

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return u"%s" % self.name

    @staticmethod
    def owner_id():
        ownerid = UserGroupType.objects.get(name=UserGroupType.OWNER).id
        return ownerid


class UserGroup(CommonInfoModel):
    name = models.CharField(max_length=200)
    type = models.ForeignKey(UserGroupType)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    # allow app to be null for company user group
    app = models.ForeignKey(App, null=True, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owned_user_groups',
                                on_delete=SET_NULL, null=True)

    def __str__(self):
        app_name = "no app"
        if self.app:
            app_name = self.app.name
        return u"%s: %s %s" % (app_name, self.type.name, self.name)

    @staticmethod
    def is_owner(user, app):
        result = False
        if UserGroup.objects.filter(type__name=UserGroupType.OWNER, app=app).count():
            members = UserGroup.objects.get(type__name=UserGroupType.OWNER, app=app).members
            if members.all().count() and user in members.all():
                result = True
        return result

    def is_app_owner_group(self):
        return self.type.name == UserGroupType.OWNER

    def is_company_group(self):
        return self.type.name == UserGroupType.COMPANY

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if not self.pk and self.type.name in (UserGroupType.ANGEL, UserGroupType.OWNER,
                                              UserGroupType.ISSUE_HANDLER) and \
                UserGroup.objects.filter(app=self.app, type=self.type).exists():
            raise ValidationError({
                'msg': 'One app should only have one {} group'.format(self.type.name)
            })

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("app", "name")
