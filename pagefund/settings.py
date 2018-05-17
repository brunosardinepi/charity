import os
import sys

from . import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = config.settings['secret_key']

DEBUG = config.settings['debug']

SERVER_EMAIL = 'no-reply@page.fund'
ADMINS = [('Garrett', 'gn9012@gmail.com')]

ALLOWED_HOSTS = config.settings['allowed_hosts']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.postgres',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',
    'lib',
    'userprofile',
    'page',
    'campaign',
    'search',
    'guardian',
    'invitations',
    'donation',
    'stripe',
    'plans',
    'webhooks',
    'faqs',
    'notes',
    'widget_tweaks',
    'comments',
    'email_templates',
    'formtools',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pagefund.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'pagefund.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config.settings['db_name'],
        'USER': config.settings['db_user'],
        'PASSWORD': config.settings['db_password'],
        'HOST': config.settings['db_host'],
        'PORT': config.settings['db_port'],
    }
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
)

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DATE_INPUT_FORMATS = ('%m-%d-%Y')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
UPLOAD_TYPES = ['image']
MAX_IMAGE_UPLOAD_SIZE = 4*1024*1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 4*1024*1024
FILE_UPLOAD_PERMISSIONS = 0o644

# allauth
SITE_ID = 1
LOGIN_REDIRECT_URL = 'home'
ACCOUNT_ADAPTER = 'userprofile.adapters.CustomAccountAdapter'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
#ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION  = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = 'home'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_USERNAME_REQUIRED = False

DEFAULT_FROM_EMAIL = 'no-reply@page.fund'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = config.settings['sendgrid_username']
EMAIL_HOST_PASSWORD = config.settings['sendgrid_password']
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# django-debug-toolbar
if DEBUG:
    if not TESTING:
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INTERNAL_IPS = ['127.0.0.1', '76.186.140.124']

# testing
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'
if TESTING:
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )

    INSTALLED_APPS.remove('stripe')

    MIGRATION_MODULES = {
        'account': None,
        'admin': None,
        'auth': None,
        'campaign': None,
        'comments': None,
        'contenttypes': None,
        'donation': None,
        'email_templates': None,
        'faqs': None,
        'guardian': None,
        'invitations': None,
        'lib': None,
        'notes': None,
        'page': None,
        'plans': None,
        'search': None,
        'sessions': None,
        'sites': None,
        'socialaccount': None,
        'userprofile': None,
        'webhooks': None,
    }