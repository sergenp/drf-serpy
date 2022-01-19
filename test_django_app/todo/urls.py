from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, PostViewSet

router = DefaultRouter()
router.register(r"post", PostViewSet, basename="post")
router.register(r"comment", CommentViewSet, basename="comment")

app_name = "todo"
urlpatterns = [path("", include(router.urls))]
