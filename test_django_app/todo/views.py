from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Comment, Post
from .serializers import drf, serps
from .serializers.serps import (
    CommentSerializer,
    CommentSerializerWrite,
    PaginationSerializer,
)


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = drf.PostSerializer

    @swagger_auto_schema(
        responses={
            200: serps.ReadOnlyPostSerializer.to_schema(many=True),
        },
    )
    def list(self, request, *args, **kwargs):
        # get your objects
        serializer = serps.ReadOnlyPostSerializer(instance=self.queryset.all(), many=True)
        # usr = User.objects.create(
        #     password="123456",
        #     username="abcdefg",
        #     first_name="SomeFirstName",
        #     last_name="SomeLastName",
        #     email="example@email.com",
        # )
        # Post.objects.create(title="ExamplePost", content="My Content", image="test.jpg", author=usr)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            200: serps.ReadOnlyPostSerializer.to_schema(many=False),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        # get your objects
        serializer = serps.ReadOnlyPostSerializer(instance=self.get_object(), many=False)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = drf.CommentSerializer

    @swagger_auto_schema(
        responses={
            200: PaginationSerializer.to_schema(serializer=CommentSerializer(many=True)),
        },
    )
    def list(self, request, *args, **kwargs):
        qs = self.queryset.all()
        serializer_class = serps.CommentSerializer(instance=qs, many=True)

        return Response(serializer_class.data)

    def create(self, request, *args, **kwargs):
        serializer = CommentSerializerWrite(data=request.data, many=True)
        comment_objs = serializer.instance

        return Response(request.data)
