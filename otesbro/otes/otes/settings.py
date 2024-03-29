"""
Django settings for otes project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path
# from otes.loader import load_credential
# Build paths inside the project like this: BASE_DIR / 'subdir'.
from otes.loader import load_credential
BASE_DIR = Path(__file__).resolve().parent.parent
SETTING_DEV_DIC = load_credential("develop")
# Build paths inside the project like this: BASE_DIR / 'subdir'.

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f&wd3jc%hz&^g3_+%sw)=o=*_9qw0t4f0vpc#zd6=lz6^5j2%0'
CRISPY_TEMPLATE_PACK = 'bootstrap3'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'storages',
    'uploader',
    'utils',
    'crispy_forms',
    'background_remover',
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

ROOT_URLCONF = 'otes.urls'

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

WSGI_APPLICATION = 'otes.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': SETTING_DEV_DIC["default"],
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# REST FRAMEWORK CONFIGURATION
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 50
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


# # AWS
AWS_ACCESS_KEY_ID = SETTING_DEV_DIC['S3']['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = SETTING_DEV_DIC['S3']['AWS_SECRET_ACCESS_KEY']
AWS_DEFAULT_ACL = SETTING_DEV_DIC['S3']['AWS_DEFAULT_ACL']
AWS_S3_REGION_NAME = SETTING_DEV_DIC['S3']['AWS_S3_REGION_NAME']
AWS_S3_SIGNATURE_VERSION = SETTING_DEV_DIC['S3']['AWS_S3_SIGNATURE_VERSION']
AWS_STORAGE_BUCKET_NAME = SETTING_DEV_DIC['S3']['AWS_STORAGE_BUCKET_NAME']

AWS_QUERYSTRING_AUTH = False
AWS_S3_HOST = 's3.%s.amazonaws.com' % AWS_S3_REGION_NAME

AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME)
STATIC_LOCATION = 'statics'
STATIC_URL = "https://%s/%s/" % (AWS_S3_HOST, STATIC_LOCATION)
STATICFILES_STORAGE = 'otes.storage.StaticStorage'

MEDIA_LOCATION = 'media'
MEDIA_URL = "https://%s/%s/" % (AWS_S3_HOST, MEDIA_LOCATION)

DEFAULT_FILE_STORAGE = 'otes.storage.CustomS3Boto3Storage'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_ROOT = "https://%s/statics/" % AWS_S3_CUSTOM_DOMAIN
MEDIA_ROOT = "https://%s/media/" % AWS_S3_CUSTOM_DOMAIN

LOGIN_REDIRECT_URL = '/'

