from django.urls import path, include
from dashboard.admin import custom_admin

urlpatterns = [
    path("", include('dashboard.urls')),
    path("", include("catalogue.urls")),
    path('admin/', custom_admin.urls),
]
