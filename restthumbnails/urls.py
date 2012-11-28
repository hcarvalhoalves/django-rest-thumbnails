from django.conf import settings
from django.conf.urls.defaults import patterns, url

from restthumbnails.defaults import DEFAULT_URL_REGEX
from restthumbnails.views import ThumbnailView


urlpatterns = patterns('',
    url(regex=getattr(settings, 'REST_THUMBNAILS_URL_REGEX', DEFAULT_URL_REGEX),
        view=ThumbnailView.as_view(),
        name="generate_thumbnail"),
)
