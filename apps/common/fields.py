from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text
from rest_framework import serializers


class CreatableSlugField(serializers.SlugRelatedField):
    """
    Wrapper around SlugRelatedField and provide the function to create object on the fly.
    But it's only possible to accomplish when slug field itself is enough to create the object.
    """
    default_error_messages = {
        'not_exist_and_not_created': _('Object with {slug_name}={value} does not exist and can\'t be created: {err_msg}'),
        'invalid': _('Invalid value.'),
    }

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except ObjectDoesNotExist:
            try:
                return self.get_queryset().model.objects.create(**{self.slug_field: data})
            except ValueError as e:
                self.fail('not_exist_and_not_created', slug_name=self.slug_field,
                          value=smart_text(data), err_msg=str(e))
        except (TypeError, ValueError):
            self.fail('invalid')


class ObjectSlugField(serializers.SlugRelatedField):
    """
    For the case that input is a model object, so slug field only apply to to_representation method
    """
    def to_internal_value(self, data):
        return data
