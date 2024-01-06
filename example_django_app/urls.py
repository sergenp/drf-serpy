from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API Docs",
        default_version="v1",
        description="API Documentation",
        contact=openapi.Contact(email="ozcanyd@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # noqa
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("todo.urls")),
    path("", schema_view.with_ui("swagger", cache_timeout=0)),  # noqa
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
