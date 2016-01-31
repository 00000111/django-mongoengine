from mongoengine import fields

from django_mongoengine.forms.field_generator import MongoFormFieldGenerator

class DjangoFieldMixin(object):

    def __init__(self, *args, **kwargs):
        self.editable = kwargs.pop("editable", True)
        self.blank    = kwargs.get("null", False)
        super(DjangoFieldMixin, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        return MongoFormFieldGenerator().generate(
            self, **kwargs
        )

    def save_form_data(self, instance, data):
        setattr(instance, self.name, data)

    def value_from_object(self, obj):
        return getattr(obj, self.name)

    def __eq__(self, other):
        # Needed for @total_ordering
        if isinstance(other, fields.BaseField):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other):
        # This is needed because bisect does not take a comparison function.
        if isinstance(other, fields.BaseField):
            return self.creation_counter < other.creation_counter
        return NotImplemented


import sys
current_module = sys.modules[__name__]
missing = ['EmbeddedDocument']

for f in fields.__all__ + missing:
    setattr(
        current_module, f,
        type(f, (DjangoFieldMixin, getattr(fields, f)), {
            "meta": {"abstract": True},
        })
    )
