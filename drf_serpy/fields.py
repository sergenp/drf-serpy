import importlib
import types
from datetime import date, datetime, time
from typing import Any, Callable, List, Type, Union
from urllib.parse import urljoin

from drf_yasg import openapi

settings = None  # noqa
# if django module exist, import settings from it
if importlib.util.find_spec("django.conf"):  # noqa
    # importing this will override our settings variable declared in 7th line because settings is an object
    from django.conf import settings  # noqa


class Field(object):
    """`Field` is used to define what attributes will be serialized.

    A `Field` maps a property or function on an object to a value in the
    serialized result. Subclass this to make custom fields. For most simple
    cases, overriding `Field.to_value` should give enough flexibility. If
    more control is needed, override `Field.as_getter`.

    :param str attr: The attribute to get on the object, using the same format
        as ``operator.attrgetter``. If this is not supplied, the name this
        field was assigned to on the serializer will be used.
    :param bool call: Whether the value should be called after it is retrieved
        from the object. Useful if an object has a method to be serialized.
    :param str label: A label to use as the name of the serialized field
        instead of using the attribute name of the field.
    :param bool required: Whether the field is required. If set to ``False``,
        `Field.to_value` will not be called if the value is ``None``.
    :param openapi.Schema schema_type: drf-yasg schema type of the Field, if ``None``,
        schema type of the attribute of the `Field` will be used,
    """

    #: Set to ``True`` if the value function returned from
    #: `Field.as_getter` requires the serializer to be passed in as the
    #: first argument. Otherwise, the object will be the only parameter.
    getter_takes_serializer = False

    #: Set to ``True`` if the value function returned from
    #: :meth:`Field.as_setter` requires the serializer to be passed in as the
    #: first argument. Otherwise, the object will be the only parameter.
    setter_takes_serializer = False

    # schema_type needs to be overridden by the Fields
    schema_type = None

    def __init__(
        self,
        attr: str = None,
        call: bool = False,
        label: str = None,
        required: bool = True,
        read_only: bool = False,
        schema_type: Type[openapi.Schema] = None,
    ):
        self.attr = attr
        self.call = call
        self.label = label
        self.required = required
        self.read_only = read_only or call or (attr is not None and "." in attr)
        self.schema_type = schema_type or self.schema_type

    def to_value(self, value: Type[Any]) -> Union[dict, list, bool, str, int, float]:
        """Transform the serialized value.

        Override this method to clean and validate values serialized by this
        field. For example to implement an ``int`` field: ::

            def to_value(self, value):
                return int(value)

        :param value: The value fetched from the object being serialized.
        """
        return value

    to_value._serpy_base_implementation = True

    def _is_to_value_overridden(self) -> bool:
        to_value = self.to_value
        # If to_value isn't a method, it must have been overridden.
        if not isinstance(to_value, types.MethodType):
            return True
        return not getattr(to_value, "_serpy_base_implementation", False)

    def to_internal_value(self, data: Type[Any]) -> Type[Any]:
        """Transform the serialized value into Python object

        Override this method to clean and validate values deserialized by this
        field. For example to implement an `int` field:
        ```py
        def to_internal_value(self, data):
            return data
        ```
        :param data: The data fetched from the object being deserialized.
        """
        return data

    to_internal_value._serpy_base_implementation = True

    def _is_to_internal_value_overridden(self) -> bool:
        to_internal_value = self.to_internal_value
        # If to_internal_value isn't a method, it must have been overridden.
        if not isinstance(to_internal_value, types.MethodType):
            return True
        return not getattr(to_internal_value, "_serpy_base_implementation", False)

    def as_getter(self, serializer_field_name: str, serializer_cls: Type["Serializer"]):
        """Returns a function that fetches an attribute from an object.

        Return ``None`` to use the default getter for the serializer defined in
        :attr:`Serializer.default_getter`.

        When a `Serializer` is defined, each `Field` will be
        converted into a getter function using this method. During
        serialization, each getter will be called with the object being
        serialized, and the return value will be passed through
        `Field.to_value`.

        If a `Field` has ``getter_takes_serializer = True``, then the
        getter returned from this method will be called with the
        `Serializer` instance as the first argument, and the object
        being serialized as the second.

        :param str serializer_field_name: The name this field was assigned to
            on the serializer.
        :param serializer_cls: The `Serializer` this field is a part of.
        """
        return None

    def as_setter(self, serializer_field_name: str, serializer_cls: Type["Serializer"]):
        """Returns a function that sets an attribute on an object

        Return ``None`` to use the default setter for the serializer defined in
        :attr:`Serializer.default_setter`.

        When a `Serializer` is defined, each `Field` will be
        converted into a setter function using this method. During
        deserialization, each setter will be called with the object being
        deserialized with the argument passed as the return value of
        :meth:`Field.to_internal_value`.

        If a `Field` has ``setter_takes_serializer = True``, then the
        setter returned from this method will be called with the
        `Serializer` instance as the first argument, and the object
        being serialized as the second.

        :param str serializer_field_name: The name this field was assigned to
            on the serializer.
        :param serializer_cls: The `Serializer` this field is a part of.
        """
        return None

    def get_schema(self) -> Union[None, openapi.Schema]:
        """get the openapi.Schema of the field

        Returns:
            Union[None, openapi.Schema]: return the openapi.Schema for the given schema_type
        """
        if not self.schema_type:
            return
        return openapi.Schema(
            type=self.schema_type,
        )


class StrField(Field):
    """A `Field` that converts the value to a string."""

    to_value = staticmethod(str)
    to_internal_value = staticmethod(str)
    schema_type = openapi.TYPE_STRING


class IntField(Field):
    """A `Field` that converts the value to an integer."""

    to_value = staticmethod(int)
    to_internal_value = staticmethod(int)
    schema_type = openapi.TYPE_INTEGER


class FloatField(Field):
    """A `Field` that converts the value to a float."""

    to_value = staticmethod(float)
    to_internal_value = staticmethod(float)
    schema_type = openapi.TYPE_NUMBER


class BoolField(Field):
    """A `Field` that converts the value to a boolean."""

    to_value = staticmethod(bool)
    to_internal_value = staticmethod(bool)
    schema_type = openapi.TYPE_BOOLEAN


class MethodField(Field):
    """A `Field` that calls a method on the `Serializer`.

    This is useful if a `Field` needs to serialize a value that may come
    from multiple attributes on an object. For example:
    ```py
    class FooSerializer(Serializer):
        plus = MethodField()
        minus = MethodField('do_minus')

        def get_plus(self, foo_obj) -> int:
            return foo_obj.bar + foo_obj.baz

        def do_minus(self, foo_obj) -> int:
            return foo_obj.bar - foo_obj.baz

    foo = Foo(bar=5, baz=10)
    FooSerializer(foo).data
    # {'plus': 15, 'minus': -5}
    ```
    :param str method: The method on the serializer to call. Defaults to
        ``'get_<field name>'``.
    """

    getter_takes_serializer = True
    getter_takes_serializer = True

    def __init__(self, getter: str = None, setter: str = None, **kwargs):
        assert (
            kwargs.pop("schema_type", None) is None
        ), f"MethodField doesn't take a schema_type param, use type annotations in your methods to generate schema"
        super(MethodField, self).__init__(**kwargs)
        self.getter_method = getter
        self.setter_method = setter

    def as_getter(self, serializer_field_name: str, serializer_cls: Type[Field]) -> Callable:
        method_name = self.getter_method
        if method_name is None:
            method_name = f"get_{serializer_field_name}"
        return getattr(serializer_cls, method_name)

    def as_setter(self, serializer_field_name, serializer_cls):
        method_name = self.setter_method
        if method_name is None:
            method_name = f"set_{serializer_field_name}"
        return super().as_setter(serializer_field_name, serializer_cls)


class ImageField(Field):
    """A `Field` that converts the value to a image url."""

    schema_type = openapi.TYPE_STRING
    to_internal_value = staticmethod(str)

    def __init__(self, base_url: str = None, **kwargs):
        super().__init__(**kwargs)
        if base_url is None:
            base_url = getattr(settings, "SERPY_IMAGE_FIELD_DOMAIN", "")

        self.base_url = base_url

    def to_value(self, value: Union[Type[Any], str]) -> str:
        # if given value has "url" attribute get the url from hat attribute
        # (this happens if the ORM is Django, and the given `value`` is of type ImageFıeld)
        # otherwise get the value itself
        # (this happens if you used SQLAlchemy and recorded the image as a relative url to the db)
        url = getattr(value, "url", value)
        return urljoin(self.base_url, url)


class ListField(Field):

    to_internal_value = staticmethod(list)

    def __init__(self, field_attr: str, field_type: Type[Field], **kwargs):
        assert (
            field_type.schema_type is not None
        ), f"ListField's field `{field_type}` doesn't have a declared schema type"
        super().__init__(**kwargs)
        self.field_attr = field_attr
        self.field_type = field_type

    def to_value(
        self, value: List[Union[Type[Any], bool, str, float, int]]
    ) -> List[Union[str, int, bool, float]]:
        """
        :param list value: List of self.field_attrs or list of primitive types
        """
        if self.field_type == ImageField:
            return [ImageField().to_value(getattr(v, self.field_attr, v)) for v in value]
        return [getattr(v, self.field_attr, v) for v in value]

    def get_schema(self) -> Type[openapi.Schema]:
        return openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=self.field_type.schema_type),  # noqa
        )


class DateField(Field):
    """A `Field` that converts the value to a date format."""

    date_format = "%Y-%m-%d"
    schema_type = openapi.TYPE_STRING

    def __init__(self, date_format: str = None, **kwargs):
        super().__init__(**kwargs)
        self.date_format = date_format or self.date_format

    def to_value(self, value: Union[datetime, time, date]) -> str:
        if value:
            return value.strftime(self.date_format)

    def to_internal_value(self, value: str) -> datetime:
        if value:
            return datetime.strptime(value, self.date_format)


class DateTimeField(DateField):
    """A `Field` that converts the value to a date time format."""

    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    schema_type = openapi.TYPE_STRING
