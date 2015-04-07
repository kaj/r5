# Collect actual settings

from .defaults import *
from .local import *

# A SECRET_KEY must be declared in local.py.

# Enable django_statsd by defining STATSD_PREFIX to web.url_domain in local.py
if STATSD_PREFIX:
    MIDDLEWARE_CLASSES = (
        'django_statsd.middleware.GraphiteRequestTimingMiddleware',
        'django_statsd.middleware.GraphiteMiddleware',
        ) + MIDDLEWARE_CLASSES
    INSTALLED_APPS = (
        'django_statsd',
        ) + INSTALLED_APPS


if DEBUG_TOOLBAR:
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    from .defaults import INSTALLED_APPS, MIDDLEWARE_CLASSES
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + \
                         MIDDLEWARE_CLASSES
