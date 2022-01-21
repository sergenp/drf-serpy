# Custom Fields
*************

The most common way to create a custom field with **drf_serpy** is to override
`drf_serpy.Field.to_value`. This method is called on the value
retrieved from the object being serialized. For example, to create a field that
adds 5 to every value it serializes, do:

```python
   class Add5Field(drf_serpy.Field):
      def to_value(self, value):
         return value + 5
```
Then to use it:

```python
   class Obj(object):
      pass

   class ObjSerializer(drf_serpy.Serializer):
      foo = Add5Field()

   f = Obj()
   f.foo = 9
   ObjSerializer(f).data
   # {'foo': 14}
```

Another use for custom fields is data validation. For example, to validate that
every serialized value has a `'.'` in it:

```python
   class ValidateDotField(drf_serpy.Field):
      def to_value(self, value):
         if '.' not in value:
            raise ValidationError('no dot!')
         return value
```

For more control over the behavior of the field, override
`drf_serpy.Field.as_getter`. When the `drf_serpy.Serializer` class is
created, each field will be compiled to a getter, that will be called to get its
associated attribute from the object. For an example of this, see the
`drf_serpy.MethodField` implementation.
