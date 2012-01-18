import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG
PROD = False
USE_SSL = False

LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dashboard',
        'USER': 'dashboard',   
        'PASSWORD': 'tomato',
        'HOST': 'localhost',   
        'default-character-set': 'utf8',  
    },
}

# We recommend you use memcached for development; otherwise after every reload
# of the django development server, you will have to login again. To use
# memcached set CACHE_BACKED to something like 'memcached://127.0.0.1:11211/'
CACHE_BACKEND = 'locmem://'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'


# Send email to the console by default
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Or send them to /dev/null
#EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

MAILER_EMAIL_BACKEND = EMAIL_BACKEND

# Configure these for your outgoing email host
# EMAIL_HOST = 'smtp.my-company.com'
# EMAIL_PORT = 25
# EMAIL_HOST_USER = 'djangomail'
# EMAIL_HOST_PASSWORD = 'top-secret!'

STEER_CONFIG = {
    'dashboards': ('engine', 'syspanel', 'settings',),
    'default_dashboard': 'engine',
    'user_home': 'dashboard.views.user_home',
}

X7_HOST = "127.0.0.1"
X7_KEYSTONE_URL = "http://%s:5000/v2.0" % X7_HOST
# FIXME: this is only needed until keystone fixes its GET /tenants call
# so that it doesn't return everything for admins
X7_KEYSTONE_ADMIN_URL = "http://%s:35357/v2.0" % X7_HOST
X7_KEYSTONE_DEFAULT_ROLE = "Member"

# The number of Chase containers and objects to display on a single page before
# providing a paging element (a "more" link) to paginate results.
CHASE_PAGINATE_LIMIT = 1000

# Configure quantum connection details for networking
QUANTUM_ENABLED = True
QUANTUM_URL = '%s'  % X7_HOST
QUANTUM_PORT = '9696'
QUANTUM_TENANT = '1234'
QUANTUM_CLIENT_VERSION='0.1'

# If you have external monitoring links, eg:
# EXTERNAL_MONITORING = [
#     ['Nagios','http://foo.com'],
#     ['Ganglia','http://bar.com'],
# ]

LOGGING = {
        'version': 1,
        # When set to True this will disable all logging except
        # for loggers specified in this configuration dictionary. Note that
        # if nothing is specified here and disable_existing_loggers is True,
        # django.db.backends will still log unless it is disabled explicitly.
        'disable_existing_loggers': False,
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'django.utils.log.NullHandler',
                },
            'console': {
                # Set the level to "DEBUG" for verbose output logging.
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                },
            },
        'loggers': {
            # Logging from django.db.backends is VERY verbose, send to null
            # by default.
            'django.db.backends': {
                'handlers': ['null'],
                'propagate': False,
                },
            'steer': {
                'handlers': ['console'],
                'propagate': False,
            },
            'engineclient': {
                'handlers': ['console'],
                'propagate': False,
            },
            'keystoneclient': {
                'handlers': ['console'],
                'propagate': False,
            },
            'nose.plugins.manager': {
                'handlers': ['console'],
                'propagate': False,
            }
        }
}

# How much ram on each compute host?
COMPUTE_HOST_RAM_GB = 16
