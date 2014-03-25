from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'events.views.home', name='home'),
    url(r'^import_fb_data', 'events.views.import_fb_data', name='import_fb_data'),
    url(r'^event_list', 'events.views.list', name='event_list'),
    url(r'^event_details/(?P<id>\d+)', 'events.views.details', name='event_details'),
    # Examples:
    # url(r'^$', 'vibe.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
