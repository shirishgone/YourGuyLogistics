from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'yourguy.views.index'),
    url(r'^api/v1/', include('api.urls')),
    url(r'^api/v2/', include('api_v2.urls')),
    url(r'^admin/', include(admin.site.urls)),
)