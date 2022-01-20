from django.conf import settings

settings.configure()

import django

django.setup()

import drf_serpy
import marshmallow
from rest_framework import serializers as rf_serializers

from utils import write_csv


class SimpleRF(rf_serializers.Serializer):
    foo = rf_serializers.ReadOnlyField()


class SimpleM(marshmallow.Schema):
    foo = marshmallow.fields.Str()


class SimpleS(drf_serpy.Serializer):
    foo = drf_serpy.Field()


if __name__ == "__main__":
    data = {"foo": "bar"}
    write_csv(__file__, data, SimpleRF, SimpleM().dump, SimpleS, 100)
