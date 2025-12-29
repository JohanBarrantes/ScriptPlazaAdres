"""Main URLs module."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path(settings.ADMIN_URL, admin.site.urls),

    # Apps
    path('', include('converter.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
