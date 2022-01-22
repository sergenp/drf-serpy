from typing import List

import drf_serpy

from ..models import Comment, User


class UserSerializer(drf_serpy.Serializer):
    class Meta:
        model = User

    id = drf_serpy.IntField()
    username = drf_serpy.StrField()
    email = drf_serpy.StrField()
    first_name = drf_serpy.StrField()
    last_name = drf_serpy.StrField()


class TagSerializer(drf_serpy.Serializer):
    id = drf_serpy.IntField()
    name = drf_serpy.StrField()
    created = drf_serpy.DateTimeField()
    updated = drf_serpy.DateTimeField()


class ReadOnlyPostSerializer(drf_serpy.Serializer):
    """
    Sample description to be used in schema
    """

    id = drf_serpy.IntField()
    author = UserSerializer()
    title = drf_serpy.StrField()
    content = drf_serpy.StrField()
    image = drf_serpy.ImageField()
    tags = TagSerializer(many=True)
    created = drf_serpy.DateTimeField()
    updated = drf_serpy.DateTimeField()
    dummy = drf_serpy.MethodField()
    is_completed = drf_serpy.MethodField()

    def get_dummy(self, value) -> List[int]:
        return list(range(1, 10))

    # typing is necessary to create schema, otherwise method field schema's will default to returning str
    def get_is_completed(self, value) -> bool:
        return True


class CommentSerializer(drf_serpy.Serializer):
    class Meta:
        model = Comment

    id = drf_serpy.IntField()
    user = UserSerializer()
    post = ReadOnlyPostSerializer()
    comment = drf_serpy.StrField()
    created = drf_serpy.DateTimeField
    updated = drf_serpy.DateTimeField


class CommentSerializerWrite(drf_serpy.Serializer):
    class Meta:
        model = Comment

    comment = drf_serpy.StrField()


class LinkSerializer(drf_serpy.Serializer):
    next = drf_serpy.StrField()
    previous = drf_serpy.StrField()


class PaginationSerializer(drf_serpy.Serializer):
    links = LinkSerializer()
    count = drf_serpy.IntField()
    current_page = drf_serpy.IntField()
    page_size = drf_serpy.IntField()
    results = drf_serpy.Serializer()
