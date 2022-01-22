import operator
from collections import Iterable
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
    pass


@staticmethod
def attrsetter(attr_name):
    """
    attrsetter(attr) --> attrsetter object

    Return a callable object that sets the given attribute(s) on its first
    operand as the second operand
    After f = attrsetter('name'), the call f(o, val) executes: o.name = val
    """

    def _attrsetter(obj, val):
        setattr(obj, attr_name, val)

    return _attrsetter


def _compile_read_field_to_tuple(
    field: Type[Field], name: str, serializer_cls: Type["Serializer"]
) -> Tuple:
    getter = field.as_getter(name, serializer_cls)
    if getter is None:
        getter = serializer_cls._meta.default_getter(field.attr or name)

    # Only set a to_value function if it has been overridden for performance.
    to_value = None
    if field._is_to_value_overridden():
        to_value = field.to_value

    # Set the field name to a supplied label; defaults to the attribute name.
    name = field.label or name

    return (name, getter, to_value, field.call, field.required, field.getter_takes_serializer)


def _compile_write_field_to_tuple(field, name, serializer_cls):
    setter = field.as_setter(name, serializer_cls)
    if setter is None:
        setter = serializer_cls._meta.default_setter(field.attr or name)

    # Only set a to_internal_value function if it has been overridden
    # for performance.
    to_internal_value = None
    if field._is_to_internal_value_overridden():
        to_internal_value = field.to_internal_value

    return (
        name,
        setter,
        to_internal_value,
        field.call,
        field.required,
        field.setter_takes_serializer,
    )


class SerializerMeta(type):
    @staticmethod
    def _compile_meta(
        direct_fields: dict,
        serializer_meta: Type["SerializerMeta"],
        serializer_cls: Type["Serializer"],
    ):
        field_map = {}
        meta_bases = ()
        # Get all the fields from base classes.
        for cls in serializer_cls.__bases__[::-1]:
            if issubclass(cls, SerializerBase) and cls is not SerializerBase:
                field_map.update(cls._meta._field_map)
                meta_bases = meta_bases + (type(cls._meta),)
        field_map.update(direct_fields)
        if serializer_meta:
            meta_bases = meta_bases + (serializer_meta,)

        # get the right order of meta bases
        meta_bases = meta_bases[::-1]

        compiled_read_fields = [
            _compile_read_field_to_tuple(field, name, serializer_cls)
            for name, field in field_map.items()
        ]

        compiled_write_fields = [
            _compile_write_field_to_tuple(field, name, serializer_cls)
            for name, field in field_map.items()
            if not field.read_only
        ]

        # automatically create an inner-class Meta that inherits from
        # parent class's inner-class Meta
        Meta = type("Meta", meta_bases, {})
        meta = Meta()
        meta._field_map = field_map
        meta._compiled_read_fields = compiled_read_fields
        meta._compiled_write_fields = compiled_write_fields

        return meta

    def __new__(cls, name: str, bases: Tuple, attrs: Dict) -> Type["SerializerMeta"]:
        # Fields declared directly on the class.
        direct_fields = {}

        # Take all the Fields from the attributes.
        for attr_name, field in attrs.items():
            if isinstance(field, Field):
                direct_fields[attr_name] = field
        for k in direct_fields.keys():
            del attrs[k]

        serializer_meta = attrs.pop("Meta", None)

        real_cls = super(SerializerMeta, cls).__new__(cls, name, bases, attrs)

        real_cls._meta = cls._compile_meta(direct_fields, serializer_meta, real_cls)

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

    class Meta:
        model = None
        #: The default getter used if :meth:`Field.as_getter` returns None.
        default_getter = operator.attrgetter
        default_setter = attrsetter

    def __init__(
        self,
        instance: Type[Any] = None,
        many: bool = False,
        data: dict = None,
        context: dict = None,
        **kwargs,
    ):
        super(Serializer, self).__init__(**kwargs)
        self._can_serialize = instance is not None
        self._can_deserialize = not self._can_serialize and data is not None
        if self._can_serialize:
            self._initial_instance = instance
            self._data = None
        elif self._can_deserialize:
            self._initial_data = data
            self._instance = None
        self.many = many
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

    def _deserialize(self, data, fields):
        v = self._meta.model()
        for name, setter, to_internal, call, required, pass_self in fields:
            if pass_self:
                setter(self, v, data[name])
            else:
                if required:
                    value = data[name]
                else:
                    value = data.get(name)
                if to_internal and (required or value is not None):
                    value = to_internal(value)
                setter(v, value)
        return v

    def to_value(self, instance: Type[Any]) -> Union[Dict, List]:
        fields: Tuple = self._meta._compiled_read_fields

        if self.many:
            serialize = self._serialize
            # django orm support for m2m fields
            if getattr(instance, "iterator", None):
                return [serialize(o, fields) for o in instance.iterator()]
            return [serialize(o, fields) for o in instance]
        return self._serialize(instance, fields)

    def to_internal_value(self, data):
        fields = self._meta._compiled_write_fields
        if self.many:
            deserialize = self._deserialize
            return [deserialize(o, fields) for o in data]
        return self._deserialize(data, fields)

    @classmethod
    def to_schema(cls: SerializerMeta, many: bool = False, *args, **kwargs) -> openapi.Response:
        properties = {}
        maps = cls._meta._field_map
        for name, getter, *_ in cls._meta._compiled_read_fields:
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
            self._data = self.to_value(self._initial_instance)
        return self._data

    @property
    def instance(self) -> Union[Type["self._meta.model"], List[Type["self._meta.model"]]]:
        """Get the deserialized value from the `Serializer`.

        The return value will be cached for future accesses.
        """
        # Cache the deserialized_value for next time .deserialized_value is
        # called.
        if self._instance is None:
            self._instance = self.to_internal_value(self._initial_data)
        return self._instance


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

    class Meta:
        default_getter = operator.itemgetter
