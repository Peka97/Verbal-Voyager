import os

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verbalvoyager.settings_ci')

DEBUG = False

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
    'django_recaptcha',  # Recaptcha

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

WSGI_APPLICATION = 'verbalvoyager.wsgi.application'

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'verbalvoyagertest',
            'USER': os.getenv('PSQL_USER'),
            'PASSWORD': os.getenv('PSQL_PSWD'),
            'HOST': 'localhost',
            'PORT': '5432',
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
EMAIL_HOST_USER = os.getenv('EMAIL_LOGIN')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PSWD')

# Logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'console': {
            'format': '%(name)-12s [%(levelname)-8s] %(name)s::%(module)s::%(lineno)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', ],
            'level': 'ERROR',
            'propagate': True
        },
        'django.request': {
            'handlers': ['console', ],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

SITE_NAME = 'https://verbal-voyager.ru'
