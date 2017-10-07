# Collect actual settings

from .defaults import *
from .local import *

# A SECRET_KEY must be declared in local.py.

if DEBUG_TOOLBAR:
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': 'blog.views.debug_toolbar_enabled'
    }
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + \
                         MIDDLEWARE_CLASSES

if PROD:
    # Set a bunch of security headers
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 3600 # TODO maybe 31536000 when confirmed
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # Allow h2o proxying
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
