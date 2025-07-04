import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('DEBUG')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

INTERNAL_IPS = os.getenv('INTERNAL_IPS').split(',')

# CSRF
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS').split(',')

# Application definition
INSTALLED_APPS = [
    # New Admin UI
    # "admin_interface",
    # "colorfield",

    # Default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Libraries
    'rangefilter',  # Django Admin range filters
    'fontawesomefree',  # CSS static
    'nested_admin',  # Django Admin multiinlines
    'django_recaptcha',  # Recaptcha
    'django_json_widget',  # Django Admin JSON Widget

    # Created
    'users',
    'pages',
    'dictionary',
    'exercises',
    'exercise_result',
    'event_calendar',
    'lesson_plan',
    'logging_app',
    'constructor',
]

# X_FRAME_OPTIONS = "SAMEORIGIN"
# SILENCED_SYSTEM_CHECKS = ["security.W019"]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.TimezoneMiddleware'
]

if DEBUG:
    INSTALLED_APPS = [
        *INSTALLED_APPS,
        'debug_toolbar',
    ]
    MIDDLEWARE = [
        *MIDDLEWARE,
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

ROOT_URLCONF = 'verbalvoyager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },

    },
]

# Enable Django Admin Tools
if os.getenv('ADMIN_TOOLS_ENABLE') is True:
    INSTALLED_APPS = [
        'admin_tools',
        'admin_tools.theming',
        'admin_tools.menu',
        'admin_tools.dashboard',
    ] + INSTALLED_APPS

    TEMPLATES[0]['APP_DIRS'] = False
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        'admin_tools.template_loaders.Loader',
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]
    ADMIN_TOOLS_MENU = 'verbalvoyager.menu.CustomMenu'
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'verbalvoyager.dashboard.CustomAppIndexDashboard'

WSGI_APPLICATION = 'verbalvoyager.wsgi.application'

if DEBUG:
    DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'TEST': {
            'NAME': os.getenv('DB_TEST_NAME'),
        },
    }
}

# Authentication
AUTH_USER_MODEL = 'users.User'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_URL = '/users/auth'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Recaptcha
RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')
SILENCED_SYSTEM_CHECKS = ['***_recaptcha.recaptcha_test_key_error']

# Internationalization
LANGUAGE_CODE = 'ru-ru'

USE_I18N = True
USE_L10N = True
LANGUAGES = [
    ('ru', 'Russian'),
]
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Europe/Saratov'
USE_TZ = False

# Static files (CSS, JavaScript, Images)
if DEBUG:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
else:
    # CDN
    STATIC_URL = 'https://cdn.verbal-voyager.ru/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    STATICFILES_STORAGE = 'flexible_manifest_staticfiles.storage.ManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# Redis
CACHES = {
    "default": {
        "BACKEND": os.getenv("REDIS_BACKEND"),
        # 'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        "LOCATION": os.getenv("REDIS_DEFAULT_LOCATION"),
        "OPTIONS": {
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "VERSION": os.getenv("REDIS_VERSION"),
            "SSL": not DEBUG,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "retry_on_timeout": True,
            },
            "COMPRESS_MIN_LENGTH": 500,
        },
        "KEY_PREFIX": os.getenv("REDIS_DEFAULT_PREFIX"),
        "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_SESSION_LOCATION"),
        "OPTIONS": {
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "VERSION": os.getenv("REDIS_VERSION"),
            "SSL": not DEBUG,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "retry_on_timeout": True,
            },
            "COMPRESS_MIN_LENGTH": 500,
        },
        "KEY_PREFIX": os.getenv("REDIS_SESSION_PREFIX"),
        "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_REDIS_MAX_ENTRIES = 10000
SESSION_REDIS_EXPIRE = SESSION_COOKIE_AGE
REDIS_METRICS_ENABLED = True

if DEBUG:
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE = True

if DEBUG:
    from django.core.cache import cache
    cache.clear()

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Вывод писем в консоль
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_SSL = True
EMAIL_TIMEOUT = 15
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
        },
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'django_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.getenv('LOGGING_DJANGO_FILE_FP'),
            'formatter': 'default'
        },
        'words_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.getenv('LOGGING_WORDS_FILE_FP'),
            'formatter': 'default'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django_file'],
            'level': 'ERROR',
            'propagate': True
        },
        'django.request': {
            'handlers': ['console', 'django_file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'words': {
            'handlers': ['words_file',],
            'level': 'INFO',
            'propagate': False,
        },
    }
}


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

SITE_NAME = os.getenv('SITE_NAME')
SITE_ID = 1
