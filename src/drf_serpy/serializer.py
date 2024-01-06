import operator
from collections.abc import Iterable
from typing import Any, Dict, List, Tuple, Type, Union

from drf_yasg import openapi

from drf_serpy.fields import Field, MethodField

SCHEMA_MAPPER = {
    str: openapi.TYPE_STRING,
    int: openapi.TYPE_INTEGER,
    float: openapi.TYPE_NUMBER,
    bool: openapi.TYPE_BOOLEAN,
}


class SerializerBase(Field):
    _field_map = {}


def _compile_field_to_tuple(
    field: Type[Field], name: str, serializer_cls: Type["Serializer"]
) -> Tuple:
    getter = field.as_getter(name, serializer_cls)
    if getter is None:
        getter = serializer_cls.default_getter(field.attr or name)

    # Only set a to_value function if it has been overridden for performance.
    to_value = None
    if field._is_to_value_overridden():
        to_value = field.to_value

    # Set the field name to a supplied label; defaults to the attribute name.
    name = field.label or name

    return (
        name,
        getter,
        to_value,
        field.call,
        field.required,
        field.getter_takes_serializer,
    )


class SerializerMeta(type):
    @staticmethod
    def _get_fields(direct_fields: Dict, serializer_cls: Type["Serializer"]):
        field_map = {}
        # Get all the fields from base classes.
        for cls in serializer_cls.__mro__[::-1]:
            if issubclass(cls, SerializerBase):
                field_map.update(cls._field_map)
        field_map.update(direct_fields)
        return field_map

    @staticmethod
    def _compile_fields(field_map: Dict, serializer_cls: Type["Serializer"]):
        return [
            _compile_field_to_tuple(field, name, serializer_cls)
            for name, field in field_map.items()
        ]

    def __new__(cls, name: str, bases: Tuple, attrs: Dict) -> Type["SerializerMeta"]:
        # Fields declared directly on the class.
        direct_fields = {}

        # Take all the Fields from the attributes.
        for attr_name, field in attrs.items():
            if isinstance(field, Field):
                direct_fields[attr_name] = field
        for k in direct_fields.keys():
            del attrs[k]

        real_cls = super(SerializerMeta, cls).__new__(cls, name, bases, attrs)

        field_map = cls._get_fields(direct_fields, real_cls)
        compiled_fields = cls._compile_fields(field_map, real_cls)

        real_cls._field_map = field_map
        real_cls._compiled_fields = tuple(compiled_fields)
        return real_cls


class Serializer(SerializerBase, metaclass=SerializerMeta):
    """`Serializer` is used as a base for custom serializers.

    The `Serializer` class is also a subclass of `Field`, and can
    be used as a `Field` to create nested schemas. A serializer is
    defined by subclassing `Serializer` and adding each `Field`
    as a class variable:

    Example:
    ````py
    class FooSerializer(Serializer):
        foo = Field()
        bar = Field()

    foo = Foo(foo='hello', bar=5)
    FooSerializer(foo).data
    # {'foo': 'hello', 'bar': 5}
    ```
    :param instance: The object or objects to serialize.
    :param bool many: If ``instance`` is a collection of objects, set ``many``
        to ``True`` to serialize to a list.
    :param dict context: Currently unused parameter for compatability with Django
        REST Framework serializers.
        you can manually pass the context in and use it on the functions like as a runtime attribute
    """

    #: The default getter used if :meth:`Field.as_getter` returns None.
    default_getter = operator.attrgetter

    def __init__(
        self,
        instance: Type[Any] = None,
        many: bool = False,
        data: dict = None,
        context: dict = None,
        **kwargs,
    ):
        if data is not None:
            raise RuntimeError("serpy serializers do not support input validation")

        super(Serializer, self).__init__(**kwargs)
        self.instance = instance
        self.many = many
        self._data = None
        self.context = context

    def _serialize(self, instance: Type[Any], fields: Tuple):
        v = {}
        for name, getter, to_value, call, required, pass_self in fields:
            if pass_self:
                result = getter(self, instance)
            else:
                try:
                    result = getter(instance)
                except (KeyError, AttributeError):
                    if required:
                        raise
                    else:
                        continue
                if required or result is not None:
                    if call:
                        result = result()
                    if to_value:
                        result = to_value(result)
            v[name] = result

        return v

    def to_value(self, instance: Type[Any]) -> Union[Dict, List]:
        fields: Tuple = self._compiled_fields

        if self.many:
            serialize = self._serialize
            # django orm support for m2m fields
            if getattr(instance, "iterator", None):
                return [serialize(o, fields) for o in instance.iterator()]
            return [serialize(o, fields) for o in instance]
        return self._serialize(instance, fields)

    @classmethod
    def to_schema(
        cls: SerializerMeta, many: bool = False, *args, **kwargs
    ) -> openapi.Response:
        properties = {}
        maps = cls._field_map
        for name, getter, *_ in cls._compiled_fields:
            field = maps[name]
            if isinstance(field, Serializer):
                # this is for using a blank serializer.Serializer class
                # in your serpy Serializers to generate schema without
                #  depending on one single serializer
                if type(field) is Serializer:
                    field = kwargs.get("serializer")

                if field.many:
                    properties[name] = openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        title=field.__class__.__name__,
                        items=openapi.Items(  # noqa
                            type=openapi.TYPE_OBJECT,
                            properties=field.to_schema().schema.properties,
                        ),
                    )
                else:
                    properties[name] = openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        title=field.__class__.__name__,
                        properties=field.to_schema().schema.properties,
                    )
            elif isinstance(field, MethodField):
                if field.schema_type:
                    properties[name] = field.get_schema()
                    continue

                return_type = getter.__annotations__.get("return", None)
                assert (
                    return_type is not None
                ), f"Declare a return type annotation for field `{name}` of {cls}!"
                if return_type in SCHEMA_MAPPER.keys():
                    properties[name] = openapi.Schema(type=SCHEMA_MAPPER[return_type])
                    continue

                # TODO: check if the method's return type is:
                #  instance of SerializerMeta
                #  instance of primitive iterables except str
                #  instance of typing module types

                # if the return type is not mapped to primitive types
                # check if it is of type List[Union[bool,str,int,float]]
                # if it is a List of any other non-primitive types, it will show up as
                # List[str] in the openapi schema
                if hasattr(return_type, "__origin__"):
                    if issubclass(return_type.__origin__, Iterable):
                        arg = return_type.__args__[0]
                        properties[name] = openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(  # noqa
                                type=SCHEMA_MAPPER.get(arg, openapi.TYPE_STRING)
                            ),
                        )
            else:
                properties[name] = field.get_schema()

        if many:
            schema = openapi.Schema(
                title=cls.__mro__[0].__name__,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(  # noqa
                    type=openapi.TYPE_OBJECT,
                    properties=properties,
                ),
            )
        else:
            schema = openapi.Schema(
                title=cls.__mro__[0].__name__,
                type=openapi.TYPE_OBJECT,
                properties=properties,
            )
        return openapi.Response(cls.__mro__[0].__doc__, schema=schema)

    @property
    def data(self) -> Dict:
        """Get the serialized data from the `Serializer`.

        The data will be cached for future accesses.
        """
        # Cache the data for next time .data is called.
        if self._data is None:
            self._data = self.to_value(self.instance)
        return self._data


class DictSerializer(Serializer):
    """`DictSerializer` serializes python ``dicts`` instead of objects.

    Instead of the serializer's fields fetching data using
    ``operator.attrgetter``, `DictSerializer` uses
    ``operator.itemgetter``.

    Example:
    ```py
    class FooSerializer(DictSerializer):
        foo = IntField()
        bar = FloatField()

    foo = {'foo': '5', 'bar': '2.2'}
    FooSerializer(foo).data
    # {'foo': 5, 'bar': 2.2}
    ```
    """

    default_getter = operator.itemgetter
