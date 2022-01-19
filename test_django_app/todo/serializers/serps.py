from typing import List

import serpy


class UserSerializer(serpy.Serializer):
    id = serpy.IntField()
    username = serpy.StrField()
    email = serpy.StrField()
    first_name = serpy.StrField()
    last_name = serpy.StrField()


class TagSerializer(serpy.Serializer):
    id = serpy.IntField()
    name = serpy.StrField()
    created = serpy.DateTimeField()
    updated = serpy.DateTimeField()


class ReadOnlyPostSerializer(serpy.Serializer):
    """
    Sample description to be used in schema
    """

    id = serpy.IntField()
    author = UserSerializer()
    title = serpy.StrField()
    content = serpy.StrField()
    image = serpy.ImageField()
    tags = TagSerializer(many=True)
    created = serpy.DateTimeField()
    updated = serpy.DateTimeField()
    dummy = serpy.MethodField()
    is_completed = serpy.MethodField()

    def get_dummy(self, value) -> List[int]:
        return list(range(1, 10))

    # typing is necessary to create schema, otherwise method field schema's will default to returning str
    def get_is_completed(self, value) -> bool:
        return True


class CommentSerializer(serpy.Serializer):
    id = serpy.IntField()
    user = UserSerializer()
    post = ReadOnlyPostSerializer()
    comment = serpy.StrField()
    created = serpy.DateTimeField()
    updated = serpy.DateTimeField()
