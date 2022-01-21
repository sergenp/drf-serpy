# drf_serpy.Fields

- [drf_serpy.Fields](#drf_serpyfields)
  - [Field Objects](#field-objects)
      - [getter\_takes\_serializer](#getter_takes_serializer)
      - [to\_value](#to_value)
      - [as\_getter](#as_getter)
      - [get\_schema](#get_schema)
  - [StrField Objects](#strfield-objects)
  - [IntField Objects](#intfield-objects)
  - [FloatField Objects](#floatfield-objects)
  - [BoolField Objects](#boolfield-objects)
  - [MethodField Objects](#methodfield-objects)
  - [ImageField Objects](#imagefield-objects)
  - [ListField Objects](#listfield-objects)
      - [to\_value](#to_value-1)
  - [DateField Objects](#datefield-objects)
  - [DateTimeField Objects](#datetimefield-objects)

<a id="drf_serpy.fields.Field"></a>

## Field Objects

```python
class Field(object)
```

**Arguments**:

- `attr` (`str`): The attribute to get on the object, using the same format
as ``operator.attrgetter``. If this is not supplied, the name this
field was assigned to on the serializer will be used.
- `call` (`bool`): Whether the value should be called after it is retrieved
from the object. Useful if an object has a method to be serialized.
- `label` (`str`): A label to use as the name of the serialized field
instead of using the attribute name of the field.
- `required` (`bool`): Whether the field is required. If set to ``False``,
:meth:`Field.to_value` will not be called if the value is ``None``.
- `schema_type` (`openapi.Schema`): drf-yasg schema type of the Field, if ``None``,
schema type of the attribute of the `Field` will be used,

<a id="drf_serpy.fields.Field.getter_takes_serializer"></a>

#### getter\_takes\_serializer

Set to ``True`` if the value function returned from
:meth:`Field.as_getter` requires the serializer to be passed in as the
first argument. Otherwise, the object will be the only parameter.

<a id="drf_serpy.fields.Field.to_value"></a>

#### to\_value

```python
def to_value(value: Type[Any]) -> Union[dict, list, bool, str, int, float]
```

Transform the serialized value.

Override this method to clean and validate values serialized by this
field. For example to implement an ``int`` field: ::

    def to_value(self, value):
        return int(value)

**Arguments**:

- `value`: The value fetched from the object being serialized.

<a id="drf_serpy.fields.Field.as_getter"></a>

#### as\_getter

```python
def as_getter(serializer_field_name: str, serializer_cls: Type["Serializer"])
```

Returns a function that fetches an attribute from an object.

Return ``None`` to use the default getter for the serializer defined in

**Arguments**:

- `serializer_field_name` (`str`): The name this field was assigned to
on the serializer.
- `serializer_cls`: The `Serializer` this field is a part of.

<a id="drf_serpy.fields.Field.get_schema"></a>

#### get\_schema

```python
def get_schema() -> Union[None, openapi.Schema]
```

get the openapi.Schema of the field

**Returns**:

  Union[None, openapi.Schema]: return the openapi.Schema for the given schema_type

<a id="drf_serpy.fields.StrField"></a>

## StrField Objects

```python
class StrField(Field)
```

A `Field` that converts the value to a string.

<a id="drf_serpy.fields.IntField"></a>

## IntField Objects

```python
class IntField(Field)
```

A `Field` that converts the value to an integer.

<a id="drf_serpy.fields.FloatField"></a>

## FloatField Objects

```python
class FloatField(Field)
```

A `Field` that converts the value to a float.

<a id="drf_serpy.fields.BoolField"></a>

## BoolField Objects

```python
class BoolField(Field)
```

A `Field` that converts the value to a boolean.

<a id="drf_serpy.fields.MethodField"></a>

## MethodField Objects

```python
class MethodField(Field)
```

A `Field` that calls a method on the `Serializer`.

This is useful if a `Field` needs to serialize a value that may come
from multiple attributes on an object. For example: ::

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

**Arguments**:

- `method` (`str`): The method on the serializer to call. Defaults to
``'get_<field name>'``.

<a id="drf_serpy.fields.ImageField"></a>

## ImageField Objects

```python
class ImageField(Field)
```

A `Field` that converts the value to a image url.

<a id="drf_serpy.fields.ListField"></a>

## ListField Objects

```python
class ListField(Field)
```

<a id="drf_serpy.fields.ListField.to_value"></a>

#### to\_value

```python
def to_value(value: List[Union[Type[Any], bool, str, float, int]]) -> List[Union[str, int, bool, float]]
```

**Arguments**:

- `value` (`list`): List of self.field_attrs or list of primitive types

<a id="drf_serpy.fields.DateField"></a>

## DateField Objects

```python
class DateField(Field)
```

A `Field` that converts the value to a date format.

<a id="drf_serpy.fields.DateTimeField"></a>

## DateTimeField Objects

```python
class DateTimeField(DateField)
```

A `Field` that converts the value to a date time format.

