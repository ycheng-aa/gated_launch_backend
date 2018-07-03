from django.db import models

from gated_launch_backend import settings


class Usage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='usages')
    resource = models.CharField(max_length=300)
    method = models.CharField(max_length=10)
    link_from = models.CharField(max_length=30, null=True, blank=True)
    params = models.TextField(null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    response_http_status = models.IntegerField(null=True, blank=True)
    response_business_status = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ("user__username", "resource", "method")

    def __str__(self):
        return u'%s %s %s' % (self.user, self.resource, self.method)


class EventType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    desc = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return u'%s' % self.name


class EventTracking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='events')
    type = models.ForeignKey(EventType)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u'%s_%s' % (self.user.username, self.type.name)


class Property(models.Model):
    event = models.ForeignKey(EventTracking, related_name='properties')
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    def __str__(self):
        return u'%s %s: %s' % (str(self.event), self.key, self.value)

    class Meta:
        unique_together = (('event', 'key', 'value'), )
