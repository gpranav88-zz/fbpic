from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fbpic.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    (r'^facebook/', include('django_facebook.urls')),
    (r'^accounts/', include('django_facebook.auth_urls')), #Don't add this line if you use django registration or userena for registration and auth.
    url(r'^$', 'fbpic.views.home', name='home'),
    url(r'^next$', 'fbpic.views.next', name='next'),
)