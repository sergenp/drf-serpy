from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models import Comment, Post, Tag

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "created", "updated")


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "image",
            "tags",
            "content",
            "created",
            "updated",
        )


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    post = PostSerializer()

    class Meta:
        model = Comment
        fields = ("id", "user", "post", "comment", "created", "updated")
