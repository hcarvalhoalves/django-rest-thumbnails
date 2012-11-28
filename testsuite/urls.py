from django.conf import settings
from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    # url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^thumbnails/', include('restthumbnails.urls')),
)
