from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # Language selector
    (r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^comments/', include('django.contrib.comments.urls')),
    
    # The blog app handles most urls.  Must be last.
    url(r'^', include('blog.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        # url('500', direct_to_template, {'template': '500.html'}),
        url('404', direct_to_template, {'template': '404.html'}),
    )

# And even laster:
urlpatterns += patterns(
    '',
    url(r'^(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            }),
)
