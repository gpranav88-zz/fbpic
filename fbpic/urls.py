from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings 


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fbpic.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    (r'^facebook/', include('django_facebook.urls')),
    (r'^accounts/', include('django_facebook.auth_urls')), #Don't add this line if you use django registration or userena for registration and auth.
    url(r'^$', 'fbpic.views.home'),
    url(r'^test$', 'fbpic.views.home2'),
    url(r'^(?P<zone>(batcam1|batcam2|untameable|trampoline|none))$', 'fbpic.views.home', name='home'),
    url(r'^next$', 'fbpic.views.next', name='next'),
    url(r'^tagger/(?P<zone>(batcam|untameable|trampoline))$', 'fbpic.views.tagger', name='tagger'),
    url(r'^lastuser$', 'fbpic.views.lastuser', name='lastuser'),
    url(r'^poster$', 'fbpic.views.poster', name='poster'),
    url(r'^wall_post$', 'fbpic.views.wall_post', name='wall_post'),
    url(r'^uploader$', 'fbpic.views.uploader', name='uploader'),
    url(r'^posttofb$', 'fbpic.views.untameable_poster'),
    url(r'^karan$', 'fbpic.views.karan'),
    url(r'^day2/(\d{4})/$', 'fbpic.views.reRegister')
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)