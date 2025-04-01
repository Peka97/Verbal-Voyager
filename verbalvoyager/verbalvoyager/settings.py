import os

from pathlib import Path
from config import CURRENT_CONFIG


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = CURRENT_CONFIG.SECRET_KEY

DEBUG = CURRENT_CONFIG.DEBUG

ALLOWED_HOSTS = [
    '127.0.0.1', 'localhost', '', '::1', '158.160.153.184'
]
INTERNAL_IPS = [
    '127.0.0.1',
]

# CSRF
CSRF_TRUSTED_ORIGINS = [
    'http://verbal-voyager.ru', 'http://www.verbal-voyager.ru', 'https://verbal-voyager.ru', 'https://www.verbal-voyager.ru']

# Application definition
INSTALLED_APPS = [
    # Default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Libraries
    'rangefilter',  # Django Admin range filters
    'fontawesomefree',  # CSS static
    'nested_admin',  # Django Admin multiinlines

    # Created
    'users',
    'pages',
    'dictionary',
    'exercises',
    'exercise_result',
    'event_calendar',
    'lesson_plan',
    'logging_app',
]

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
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

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
        'console': {
            'format': '%(name)-12s [%(levelname)-8s] %(name)s::%(module)s::%(lineno)s - %(message)s'
        },
        'file': {
            'format': '%(asctime)s [%(levelname)-8s] %(name)s::%(module)s::%(lineno)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': True
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

OPENAI_API_KEY = CURRENT_CONFIG.OPENAI_API_KEY

if DEBUG:
    SITE_NAME = 'http://127.0.0.1:8000'
else:
    SITE_NAME = 'https://verbal-voyager.ru'
