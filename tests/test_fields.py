from .obj import Obj
from serpy.fields import Field, MethodField, IntField, FloatField
import unittest


class TestFields(unittest.TestCase):

    def test_simple(self):
        fn = Field().to_value_fn('a', None)
        self.assertEqual(fn(Obj(a=5)), 5)

    def test_call(self):
        fn = Field(call=True).to_value_fn('a', None)
        self.assertEqual(fn(Obj(a=lambda: 5)), 5)

    def test_transform_noop(self):
        self.assertEqual(Field().transform_value(5), 5)
        self.assertEqual(Field().transform_value('a'), 'a')
        self.assertEqual(Field().transform_value(None), None)

    def test_is_transform_overriden(self):
        class TransField(Field):
            def transform_value(self, value):
                return value

        field = Field()
        self.assertFalse(Field._is_transform_overriden(field.transform_value))
        field = TransField()
        self.assertTrue(Field._is_transform_overriden(field.transform_value))
        self.assertTrue(Field._is_transform_overriden(None))
        self.assertTrue(Field._is_transform_overriden(int))

    def test_transform(self):
        class Add5Field(Field):
            def transform_value(self, value):
                return value + 5

        fn = Add5Field().to_value_fn('a', None)
        self.assertEqual(fn(Obj(a=5)), 10)

        fn = Add5Field(call=True).to_value_fn('b', None)
        self.assertEqual(fn(Obj(b=lambda: 6)), 11)

    def test_int_field(self):
        fn = IntField().to_value_fn('a', None)
        self.assertEqual(fn(Obj(a=5)), 5)
        self.assertEqual(fn(Obj(a=5.4)), 5)
        self.assertEqual(fn(Obj(a='5')), 5)

    def test_float_field(self):
        fn = FloatField().to_value_fn('a', None)
        self.assertEqual(fn(Obj(a=5.2)), 5.2)
        self.assertEqual(fn(Obj(a='5.5')), 5.5)

    def test_custom_attr(self):
        fn = Field(attr='b').to_value_fn('a', None)
        self.assertEqual(fn(Obj(b=5, a=1)), 5)

        fn = Field(attr='b', call=True).to_value_fn('a', None)
        self.assertEqual(fn(Obj(b=lambda: 5, a=1)), 5)

    def test_dotted_attr(self):
        fn = Field(attr='z.x').to_value_fn('a', None)
        self.assertEqual(fn(Obj(z=Obj(x='hi'), a=1)), 'hi')

        fn = Field(attr='z.x', call=True).to_value_fn('a', None)
        self.assertEqual(fn(Obj(z=Obj(x=lambda: 'hi'), a=1)), 'hi')

    def test_method_field(self):
        class FakeSerializer(object):
            def get_a(self, obj):
                return obj.a

            def z_sub_1(self, obj):
                return obj.z - 1

        serializer = FakeSerializer()

        fn = MethodField().to_value_fn('a', serializer)
        self.assertEqual(fn(Obj(a=3)), 3)

        fn = MethodField('z_sub_1').to_value_fn('a', serializer)
        self.assertEqual(fn(Obj(z=3)), 2)

        self.assertTrue(MethodField.uses_self)

if __name__ == '__main__':
    unittest.main()