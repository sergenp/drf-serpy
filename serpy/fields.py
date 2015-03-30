from operator import attrgetter
import types


class Field(object):
    uses_self = False

    def __init__(self, attr=None, call=False):
        self.attr = attr
        self.call = call

    def transform_value(self, value):
        return value
    transform_value._base_implementation = True

    @staticmethod
    def _is_transform_overriden(method):
        if not isinstance(method, types.MethodType):
            return True
        return not getattr(method, '_base_implementation', False)

    def to_value_fn(self, serializer_field_name, serializer_cls):
        attr_name = self.attr
        if attr_name is None:
            attr_name = serializer_field_name
        basic_getter = attrgetter(attr_name)

        transform = self.transform_value
        has_transform = self._is_transform_overriden(transform)
        if self.call:
            if has_transform:
                getter = lambda x: transform(basic_getter(x)())
            else:
                getter = lambda x: basic_getter(x)()
        elif has_transform:
            getter = lambda x: transform(basic_getter(x))
        else:
            getter = basic_getter
        return getter


class IntField(Field):
    transform_value = staticmethod(int)


class FloatField(Field):
    transform_value = staticmethod(float)


class MethodField(Field):
    uses_self = True

    def __init__(self, method=None, **kwargs):
        super(MethodField, self).__init__(**kwargs)
        self.method = method

    def to_value_fn(self, serializer_field_name, serializer_cls):
        method_name = self.method
        if method_name is None:
            method_name = 'get_%s' % serializer_field_name
        return getattr(serializer_cls, method_name)