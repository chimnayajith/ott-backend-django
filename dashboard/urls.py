from django.urls import path, re_path
from .views import stats, top_media

urlpatterns = [
    path('admin/traffic/', stats.as_view(), name='stats'),
    path('admin/top-media/', top_media.as_view(), name='top_media'),

    # fix to successfully switch to stats when using the sidebar
    re_path(r'^admin/.+/traffic/$', stats.as_view(), name='stats'),
    re_path(r'^admin/.+/top-media/$', top_media.as_view(), name='top_media'),
]
