import os

from pathlib import Path
from config import CURRENT_CONFIG


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = CURRENT_CONFIG.SECRET_KEY

DEBUG = CURRENT_CONFIG.DEBUG

ALLOWED_HOSTS = [
    '127.0.0.1', 'localhost', '', '::1', '158.160.153.184', 'verbal-voyager.ru', 'www.verbal-voyager.ru',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

# CSRF
CSRF_TRUSTED_ORIGINS = [
    'http://verbal-voyager.ru', 'http://www.verbal-voyager.ru', 'https://verbal-voyager.ru', 'https://www.verbal-voyager.ru']

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

if CURRENT_CONFIG.DEBUG:
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
if CURRENT_CONFIG.admin_tools_enabled:
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

if CURRENT_CONFIG.DEBUG:
    DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

if CURRENT_CONFIG.DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'verbalvoyagertest',
            'USER': 'django',
            'PASSWORD': 'django',
            'HOST': 'localhost',
            'PORT': '5432',
            'TEST': {
                'NAME': 'test_verbal_voyager',
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'verbalvoyager',
            'USER': 'django',
            'PASSWORD': CURRENT_CONFIG.psql_pswd,
            'HOST': 'localhost',
            'PORT': '',
            'TEST': {
                'NAME': 'test_verbal_voyager',
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
RECAPTCHA_PUBLIC_KEY = CURRENT_CONFIG.RECAPTCHA_PUBLIC_KEY
RECAPTCHA_PRIVATE_KEY = CURRENT_CONFIG.RECAPTCHA_PRIVATE_KEY

# Internationalization
LANGUAGE_CODE = 'ru-ru'

USE_I18N = True
USE_L10N = True  # Optional, but recommended (localization)
LANGUAGES = [
    ('ru', 'Russian'),  # Добавьте ваш язык
]
LOCALE_PATHS = [
    BASE_DIR / 'locale',  # Укажите путь к каталогу с переводами
]

TIME_ZONE = 'Europe/Saratov'
USE_TZ = False

# Static files (CSS, JavaScript, Images)
if CURRENT_CONFIG.DEBUG:
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

# Для корректного отображения русских имен файлов
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# Redis
CACHES = {
    "default": {
        # "BACKEND": "django_redis.cache.RedisCache",
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        "LOCATION": CURRENT_CONFIG.REDIS_DEFAULT_LOCATION,
        "OPTIONS": {
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "IGNORE_EXCEPTIONS": True,
            "PICKLE_VERSION": -1,
            "VERSION": CURRENT_CONFIG.REDIS_VERSION,
        },
        "KEY_PREFIX": "vv",
        "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CURRENT_CONFIG.REDIS_SESSION_LOCATION,
        "OPTIONS": {
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "IGNORE_EXCEPTIONS": True,
            "PICKLE_VERSION": -1,
            "VERSION": CURRENT_CONFIG.REDIS_VERSION,
        },
        "KEY_PREFIX": "vv:s",
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
if not CURRENT_CONFIG.DEBUG:
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE = True

if DEBUG:
    from django.core.cache import cache
    cache.clear()

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Вывод писем в консоль
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_TIMEOUT = 15
EMAIL_HOST_USER = CURRENT_CONFIG.email_login
EMAIL_HOST_PASSWORD = CURRENT_CONFIG.email_password

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
            'filename': CURRENT_CONFIG.DJANGO_LOG_FILE_PATH,
            'formatter': 'default'
        },
        'words_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': CURRENT_CONFIG.WORDS_LOG_FILE_PATH,
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

OPENAI_API_KEY = CURRENT_CONFIG.OPENAI_API_KEY

if DEBUG:
    SITE_NAME = 'http://127.0.0.1:8000'
else:
    SITE_NAME = 'https://verbal-voyager.ru'

SITE_ID = 1
