from django.urls import path, include
from dashboard.admin import custom_admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include('dashboard.urls')),
    path("", include("catalogue.urls")),
    path('admin/', custom_admin.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
