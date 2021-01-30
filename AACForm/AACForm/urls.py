from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
"""
URLs used on the project level
"""
urlpatterns = [
    path('super/aac/admin/', admin.site.urls),
    re_path(r'^', include('makeReports.urls')),
    path('summernote/', include('django_summernote.urls')),
    re_path(r'^api-auth/', include('rest_framework.urls')),
]
if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)