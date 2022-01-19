import importlib
import types
from urllib.parse import urljoin

from drf_yasg import openapi

settings = None  # noqa
# if django module exist, import settings from it
if importlib.util.find_spec("django.conf"):  # noqa
    # importing this will override our settings variable declared in 7th line because settings is an object
    from django.conf import settings  # noqa


class Field(object):
    """:class:`Field` is used to define what attributes will be serialized.

    A :class:`Field` maps a property or function on an object to a value in the
    serialized result. Subclass this to make custom fields. For most simple
    cases, overriding :meth:`Field.to_value` should give enough flexibility. If
    more control is needed, override :meth:`Field.as_getter`.

    :param str attr: The attribute to get on the object, using the same format
        as ``operator.attrgetter``. If this is not supplied, the name this
        field was assigned to on the serializer will be used.
    :param bool call: Whether the value should be called after it is retrieved
        from the object. Useful if an object has a method to be serialized.
    :param str label: A label to use as the name of the serialized field
        instead of using the attribute name of the field.
    :param bool required: Whether the field is required. If set to ``False``,
        :meth:`Field.to_value` will not be called if the value is ``None``.
    """

    #: Set to ``True`` if the value function returned from
    #: :meth:`Field.as_getter` requires the serializer to be passed in as the
    #: first argument. Otherwise, the object will be the only parameter.
    getter_takes_serializer = False
    schema_type = None

    def __init__(self, attr=None, call=False, label=None, required=True, schema_type=None):
        self.attr = attr
        self.call = call
        self.label = label
        self.required = required
        self.schema_type = schema_type or self.schema_type

    def to_value(self, value):
        """Transform the serialized value.

        Override this method to clean and validate values serialized by this
        field. For example to implement an ``int`` field: ::

            def to_value(self, value):
                return int(value)

        :param value: The value fetched from the object being serialized.
        """
        return value

    to_value._serpy_base_implementation = True

    def _is_to_value_overridden(self):
        to_value = self.to_value
        # If to_value isn't a method, it must have been overridden.
        if not isinstance(to_value, types.MethodType):
            return True
        return not getattr(to_value, "_serpy_base_implementation", False)

    def as_getter(self, serializer_field_name, serializer_cls):
        """Returns a function that fetches an attribute from an object.

        Return ``None`` to use the default getter for the serializer defined in
        :attr:`Serializer.default_getter`.

        When a :class:`Serializer` is defined, each :class:`Field` will be
        converted into a getter function using this method. During
        serialization, each getter will be called with the object being
        serialized, and the return value will be passed through
        :meth:`Field.to_value`.

        If a :class:`Field` has ``getter_takes_serializer = True``, then the
        getter returned from this method will be called with the
        :class:`Serializer` instance as the first argument, and the object
        being serialized as the second.

        :param str serializer_field_name: The name this field was assigned to
            on the serializer.
        :param serializer_cls: The :class:`Serializer` this field is a part of.
        """
        return None

    def get_schema(self):
        if not self.schema_type:
            return
        return openapi.Schema(
            type=self.schema_type,
        )


class StrField(Field):
    """A :class:`Field` that converts the value to a string."""

    to_value = staticmethod(str)
    schema_type = openapi.TYPE_STRING


class IntField(Field):
    """A :class:`Field` that converts the value to an integer."""

    to_value = staticmethod(int)
    schema_type = openapi.TYPE_INTEGER


class FloatField(Field):
    """A :class:`Field` that converts the value to a float."""

    to_value = staticmethod(float)
    schema_type = openapi.TYPE_NUMBER


class BoolField(Field):
    """A :class:`Field` that converts the value to a boolean."""

    to_value = staticmethod(bool)
    schema_type = openapi.TYPE_BOOLEAN


class MethodField(Field):
    """A :class:`Field` that calls a method on the :class:`Serializer`.

    This is useful if a :class:`Field` needs to serialize a value that may come
    from multiple attributes on an object. For example: ::

        class FooSerializer(Serializer):
            plus = MethodField()
            minus = MethodField('do_minus')

            def get_plus(self, foo_obj):
                return foo_obj.bar + foo_obj.baz

            def do_minus(self, foo_obj):
                return foo_obj.bar - foo_obj.baz

        foo = Foo(bar=5, baz=10)
        FooSerializer(foo).data
        # {'plus': 15, 'minus': -5}

    :param str method: The method on the serializer to call. Defaults to
        ``'get_<field name>'``.
    """

    getter_takes_serializer = True

    def __init__(self, method=None, **kwargs):
        assert (
            kwargs.pop("schema_type", None) is None
        ), f"MethodField doesn't take a schema_type param, use type annotations in your methods to generate schema"
        super(MethodField, self).__init__(**kwargs)
        self.method = method

    def as_getter(self, serializer_field_name, serializer_cls):
        method_name = self.method
        if method_name is None:
            method_name = "get_{0}".format(serializer_field_name)
        return getattr(serializer_cls, method_name)


class ImageField(Field):
    """A :class:`Field` that converts the value to a image url."""

    schema_type = openapi.TYPE_STRING

    def __init__(self, base_url=None, **kwargs):
        super().__init__(**kwargs)
        if base_url is None:
            base_url = getattr(settings, "SERPY_IMAGE_FIELD_DOMAIN", "")

        self.base_url = base_url

    def to_value(self, value):
        url = getattr(value, "url", value)
        return urljoin(self.base_url, url)


class ListField(Field):
    def __init__(self, field_attr, field_type, **kwargs):
        assert (
            field_type.schema_type is not None
        ), f"ListField's field `{field_type}` doesn't have a declared schema type"
        super().__init__(**kwargs)
        self.field_attr = field_attr
        self.field_type = field_type

    def to_value(self, value):
        if self.field_type == ImageField:
            return [ImageField().to_value(getattr(v, self.field_attr, v)) for v in value]
        return [getattr(v, self.field_attr, v) for v in value]

    def get_schema(self):
        return openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=self.field_type.schema_type),  # noqa
        )


class DateField(Field):
    """A :class:`Field` that converts the value to a date format."""

    date_format = "%Y-%m-%d"
    schema_type = openapi.TYPE_STRING

    def __init__(self, date_format=None, **kwargs):
        super().__init__(**kwargs)
        self.date_format = date_format or self.date_format

    def to_value(self, value):
        if value:
            return value.strftime(self.date_format)


class DateTimeField(DateField):
    """A :class:`Field` that converts the value to a date time format."""

    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    schema_type = openapi.TYPE_STRING
