from django.db import models
from django.contrib.auth.models import PermissionsMixin, UserManager, AbstractBaseUser
from django.core import validators
from django.db.models import SET_NULL
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from mptt import models as mptt_models

from apps.common.models import CommonInfoModel
from apps.user_group.models import UserGroupType

MAX_LENGTH = 255


class Department(mptt_models.MPTTModel):
    name = models.CharField(max_length=100)
    parent = mptt_models.TreeForeignKey('self', null=True, blank=True, related_name='children')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u"%s" % self.name


class Role(CommonInfoModel):
    from apps.utils.utils import ClassProperty
    ADMIN = 'admin'
    APP_OWNER = 'app_owner'

    name = models.CharField(max_length=100, unique=True)

    @ClassProperty
    def admin_role(cls):
        return cls.objects.get(name=cls.ADMIN)

    @ClassProperty
    def app_owner_role(cls):
        return cls.objects.get(name=cls.APP_OWNER)

    def __str__(self):
        return u"%s" % self.name


class User(AbstractBaseUser, PermissionsMixin):
    """
    Copied from django.contrib.auth.models.AbstractUser.
    The changes performed is add department info and methods
     to user
    """
    username = models.CharField(
        _('username'),
        max_length=MAX_LENGTH,
        unique=True,
        help_text=_('Required. %s characters or fewer. Letters, digits and @/./+/-/_ or / only.') % MAX_LENGTH,
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. This value may contain only '
                  'letters, numbers ' 'and @/./+/-/_ characters.')
            ),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    full_name = models.CharField(_('full name'), max_length=80, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_connected = models.DateTimeField(_('date last connected to service'), blank=True, null=True)
    department = models.ForeignKey(Department, null=True, blank=True)
    _role = models.ForeignKey(Role, null=True, blank=True, on_delete=SET_NULL)
    phone = models.CharField(max_length=20, null=True, blank=True)
    weixin_openid = models.CharField(max_length=60, null=True, blank=True, db_index=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the full name for the user.
        """
        return self.full_name

    def get_short_name(self):
        """
        Returns full name as short name for the user.
        """
        return self.full_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_all_permissions(self, obj=None):
        return sorted(super(User, self).get_all_permissions(obj))

    def is_admin(self):
        if not self.role:
            return False
        return self.role.name == Role.ADMIN

    def is_owner(self):
        if not self.role:
            return False
        return self.role.name == Role.APP_OWNER

    @property
    def direct_dep(self):
        return self.department

    @property
    def level_one_dep(self):
        return self.department.get_root() if self.department else None

    @property
    def level_two_dep(self):
        deps = self.departments
        return deps[1] if len(deps) >= 2 else None

    @property
    def departments(self):
        result = []
        if self.department:
            result = [dep for dep in self.department.get_ancestors(include_self=True)]
        return result

    @property
    def role(self):
        result = None
        if self._role and self._role.name == Role.ADMIN:
            result = self._role
        elif self.usergroup_set.filter(type__name=UserGroupType.OWNER).exists():
            result = Role.app_owner_role
        return result
