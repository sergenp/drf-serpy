## drf-serpy: ridiculously fast object serialization

[![Travis-CI](https://travis-ci.org/clarkduvall/serpy.svg?branch=master)](https://travis-ci.org/clarkduvall/serpy?branch=master)

[![Coveralls](https://coveralls.io/repos/clarkduvall/serpy/badge.svg?branch=master)](https://coveralls.io/r/clarkduvall/serpy?branch=master)

[![Documentation Status](https://readthedocs.org/projects/serpy/badge/?version=latest)](https://readthedocs.org/projects/serpy/?badge=latest)

[![PyPI version](https://badge.fury.io/py/drf-serpy.svg)](https://badge.fury.io/py/drf-serpy)

**drf-serpy** is a super simple object serialization framework built for speed. **drf-serpy** serializes complex datatypes (Django Models, custom classes, ...) to simple native types (dicts, lists, strings, ...). The native types can easily be converted to JSON or any other format needed.

The goal of **drf-serpy** is to be able to do this *simply*, *reliably*, and *quickly*. Since serializers are class based, they can be combined, extended and customized with very little code duplication. This project aims to replace the DRF serializer in terms of *deserialization*.

 Compared to other popular Python serialization frameworks like [Django Rest Framework Serializers](http://www.django-rest-framework.org/api-guide/serializers/)
**drf-serpy** is at least an [order of magnitude](http://serpy.readthedocs.org/en/latest/performance.html)
faster.

Source
------

Source at: <https://github.com/sergenp/drf-serpy>

If you want a feature, send a pull request!

Documentation
-------------

Full documentation at: <http://serpy.readthedocs.org/en/latest/>

Installation
------------

Note that this project is aimed for **Django Rest Framework** and does not intend to provide deserialization to other frameworks. Original [serpy](https://github.com/clarkduvall/serpy) repository can be used for such cases. This is mainly because of the added *drf-yasg* for swagger generation for the *drf-serpy serializers*.


```bash
$ pip install drf-serpy
```

Examples
--------

### Simple Example

```python
import drf_serpy as serpy

class Foo(object):
    """The object to be serialized."""
    y = 'hello'
    z = 9.5

    def __init__(self, x):
        self.x = x


class FooSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    x = serpy.IntField()
    y = serpy.Field()
    z = serpy.Field()

f = Foo(1)
FooSerializer(f).data
# {'x': 1, 'y': 'hello', 'z': 9.5}

fs = [Foo(i) for i in range(100)]
FooSerializer(fs, many=True).data
# [{'x': 0, 'y': 'hello', 'z': 9.5}, {'x': 1, 'y': 'hello', 'z': 9.5}, ...]
```

### Nested Example

```python
import drf_serpy as serpy

class Nestee(object):
    """An object nested inside another object."""
    n = 'hi'


class Foo(object):
    x = 1
    nested = Nestee()


class NesteeSerializer(serpy.Serializer):
    n = serpy.Field()


class FooSerializer(serpy.Serializer):
    x = serpy.Field()
    # Use another serializer as a field.
    nested = NesteeSerializer()

f = Foo()
FooSerializer(f).data
# {'x': 1, 'nested': {'n': 'hi'}}
```

### Complex Example

```python
import drf_serpy as serpy

class Foo(object):
    y = 1
    z = 2
    super_long_thing = 10

    def x(self):
        return 5


class FooSerializer(serpy.Serializer):
    w = serpy.Field(attr='super_long_thing')
    x = serpy.Field(call=True)
    plus = serpy.MethodField()

    def get_plus(self, obj):
        return obj.y + obj.z

f = Foo()
FooSerializer(f).data
# {'w': 10, 'x': 5, 'plus': 3}
```

### Inheritance Example

```python
import drf_serpy as serpy

class Foo(object):
    a = 1
    b = 2


class ASerializer(serpy.Serializer):
    a = serpy.Field()


class ABSerializer(ASerializer):
    """ABSerializer inherits the 'a' field from ASerializer.

    This also works with multiple inheritance and mixins.
    """
    b = serpy.Field()

f = Foo()
ASerializer(f).data
# {'a': 1}
ABSerializer(f).data
# {'a': 1, 'b': 2}
```

### Swagger Generation Example 

Example is available in test_django_app, you can run the app after
cloning the project.

```python
python test_django_app/manage.py runserver
```

Note that the swagger generation is for `drf_serpy.Serializer` and doesn't care about the inputted model.
i.e. the `openapi.Schema` will be generated based on the serializer attributes.

```python
import drf_serpy as serpy
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Post 
from .serializers import drf, serps

# serps.ReadOnlyPostSerializer is this:
# class ReadOnlyPostSerializer(serpy.Serializer):
#     """
#     Sample description to be used in schema
#     """
#     id = serpy.IntField()
#     author = UserSerializer()
#     title = serpy.StrField()
#     content = serpy.StrField()
#     image = serpy.ImageField()
#     tags = TagSerializer(many=True)
#     created = serpy.DateTimeField()
#     updated = serpy.DateTimeField()
#     dummy = serpy.MethodField()
#     is_completed = serpy.MethodField()

#     def get_dummy(self, value) -> List[int]:
#         return list(range(1, 10))

#     # typing is necessary to create schema, otherwise this will throw an assertion error
#     def get_is_completed(self, value) -> bool:
#         return True

class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = drf.PostSerializer

    @swagger_auto_schema(
        responses={
            200: ReadOnlyPostSerializer.to_schema(many=True),
        },
    )
    def list(self, request, *args, **kwargs):
        # get your objects
        serializer = serps.ReadOnlyPostSerializer(instance=self.queryset.all(), many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
```

Generated Swagger:
![Swagger Gen](https://raw.githubusercontent.com/sergenp/drf-serpy/dev/docs/_static/swagger_gen.PNG)

#### Generic serializer swagger generation example:

```python

# class CommentSerializer(drf_serpy.Serializer):
#     id = drf_serpy.IntField()
#     user = UserSerializer()
#     post = ReadOnlyPostSerializer()
#     comment = drf_serpy.StrField()
#     created = drf_serpy.DateTimeField()
#     updated = drf_serpy.DateTimeField()


# class LinkSerializer(drf_serpy.Serializer):
#     next = drf_serpy.StrField()
#     previous = drf_serpy.StrField()


# class PaginationSerializer(drf_serpy.Serializer):
#     links = LinkSerializer()
#     count = drf_serpy.IntField()
#     current_page = drf_serpy.IntField()
#     page_size = drf_serpy.IntField()
#     results = drf_serpy.Serializer()

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = drf.CommentSerializer

    @swagger_auto_schema(
        responses={
            200: PaginationSerializer.to_schema(serializer=CommentSerializer(many=True)),
        },
    )
    def list(self, request, *args, **kwargs):
        self.serializer_class = serps.CommentSerializer
        return super().list(request, *args, **kwargs)
```
    
Generated Swagger:

![Swagger Gen Pagination](https://raw.githubusercontent.com/sergenp/drf-serpy/dev/docs/_static/swagger_gen_pagination.PNG)


License
-------

drf-serpy is free software distributed under the terms of the MIT license.
See the [LICENSE](https://github.com/sergenp/drf-serpy/blob/master/LICENSE) file.
