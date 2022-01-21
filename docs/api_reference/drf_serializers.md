# drf_serpy.Serializer

- [drf_serpy.Serializer](#drf_serpyserializer)
  - [Serializer Objects](#serializer-objects)
      - [default\_getter](#default_getter)
      - [data](#data)
      - [to_schema](#to_schema)
  - [DictSerializer Objects](#dictserializer-objects)

<a id="drf_serpy.serializer"></a>

## Serializer Objects

```python
class Serializer(SerializerBase, metaclass=SerializerMeta)
```
Serializer` is used as a base for custom serializers.

The `Serializer` class is also a subclass of `Field`, and can
be used as a `Field` to create nested schemas. A serializer is
defined by subclassing `Serializer` and adding each `Field`
as a class variable:

Example:

```python
class FooSerializer(Serializer):
    foo = Field()
    bar = Field()

foo = Foo(foo='hello', bar=5)
FooSerializer(foo).data
# {'foo': 'hello', 'bar': 5}
```

**Arguments**:

- `instance`: The object or objects to serialize.
- `many` (`bool`): If ``instance`` is a collection of objects, set ``many``
to ``True`` to serialize to a list.
- `context` (`dict`): Currently unused parameter for compatability with Django
REST Framework serializers.
you can manually pass the context in and use it on the functions like as a runtime attribute

<a id="drf_serpy.serializer.Serializer.default_getter"></a>

#### default\_getter

The default getter used if :meth:`Field.as_getter` returns None.

<a id="drf_serpy.serializer.Serializer.data"></a>

#### data

```python
@property
def data() -> Dict
```

Get the serialized data from the `Serializer`.

The data will be cached for future accesses.

#### to_schema
```python
@classmethod
def to_schema(cls: SerializerMeta, many: bool = False, *args, **kwargs) -> openapi.Response:
```

Convert `Serializer` to `openapi.Schema`

<a id="drf_serpy.serializer.DictSerializer"></a>

## DictSerializer Objects

```python
class DictSerializer(Serializer)
```

`DictSerializer` serializes python ``dicts`` instead of objects.

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
