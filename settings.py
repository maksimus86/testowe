#encoding:UTF-8
"""
Django settings for ebook project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import os.path
import os
# Django settings for espacer project.
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = 'info@wago.infomex.net'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_PASSWORD = "SMTPwago"
EMAIL_HOST_USER = "wago"
EMAIL_PORT = "587"
EMAIL_USE_TLS = True
EMAIL_TITLE = u'WAGGO elektroniczna platforma wymiany dokumentów'
SHARE_IN_GROUP = False
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ojsmnuh_u=vzncvps5y(0we*88j-5jbp5-(9f64ao)js9vja=%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
LANGUAGE_COOKIE_NAME = "django_language"
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []
TEMPLATE_DIRS = (
    PROJECT_PATH +  "/templates/"
)

# Application definition
LOCALE_PATHS = (
    PROJECT_PATH +'/locale',
    
)
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mptt',
    'ebook_files',
    'company',
    #'django_evolution',
    'widget_tweaks',
    'password_reset',
    'ajax_select',
)
AJAX_LOOKUP_CHANNELS = {
    #  simple: search Person.objects.filter(name__icontains=q)
    'person'  : {'model': 'auth.user', 'search_field': 'username'},
    'muser'   : ('ebook.lookups', 'UserLookup')
    # define a custom lookup channel

}
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ebook.MTMiddleware.LangBasedOnUrlMiddleware',
    
)

ROOT_URLCONF = 'ebook.urls'
AUTHENTICATION_BACKENDS = (
    'ebook.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend'
)
WSGI_APPLICATION = 'ebook.wsgi.application'
MEDIA_ROOT = PROJECT_PATH +'/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'wago_dev',                      # Or path to database file if using sqlite3.
        'USER': 'wago_dev',                      # Not used with sqlite3.
        'PASSWORD': 'PutinPutin',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'pl'
LANGUAGE_CODE_TABLE = (('en-us',"English"), ("pl", "Polski"),)
LANGUAGES = (('en-us',"English"), ("pl", "Polski"),)

USE_I18N = True
LIMIT_SIZE = 53687091200
USE_L10N = True

USE_TZ = True
TIME_ZONE = 'Europe/Warsaw'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
   PROJECT_PATH + '/static/',
)
