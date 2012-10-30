from django.conf.urls.defaults import patterns, url

from restthumbnails.views import ThumbnailView


urlpatterns = patterns('',
    url(r'^(?P<source>.+)/(?P<size>.+)/(?P<method>.+)/$', ThumbnailView.as_view(), name="generate_thumbnail"),
)
