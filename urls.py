from django.conf.urls import include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from django.views.static import serve

urlpatterns = [
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # Language selector
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

urlpatterns += [
    # The blog app handles most urls.  Must be last.
    url(r'^', include('blog.urls')),
]

if settings.DEBUG:
    from django.views.generic.base import TemplateView
    urlpatterns += [
        # url('500', TemplateView.as_view(template_name='500.html')),
        url('404', TemplateView.as_view(template_name='404.html')),
    ]

# And even laster:
urlpatterns += [
    url(r'^(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
            }),
]
