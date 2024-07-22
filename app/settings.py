from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

base_url = 'http://127.0.0.1:8000'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ei3*w6za(x1%p=0sy)2r5cs1!%-gsst+u)5pyam1k!d4x$*l93'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    "catalogue",
    'django.contrib.admin',
    'dashboard',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
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

ROOT_URLCONF = 'app.urls'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

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

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DJANGO_VECTOR_DB = {
    "DEFAULT_EMBEDDING_CLASS": "vectordb.embedding_functions.SentenceTransformerEncoder",
    "DEFAULT_EMBEDDING_MODEL": "all-MiniLM-L6-v2",
    "DEFAULT_EMBEDDING_SPACE": "l2", # Can be "cosine" or "l2"
    "DEFAULT_EMBEDDING_DIMENSION": 384, # Default is 384 for "all-MiniLM-L6-v2"
    "DEFAULT_MAX_N_RESULTS": 10, # Number of results to return from search maximum is default is 10
    "DEFAULT_MIN_SCORE": 0.0, # Minimum score to return from search default is 0.0
    "DEFAULT_MAX_BRUTEFORCE_N": 10_000, # Maximum number of items to search using brute force default is 10_000. 
    # If the number of items is greater than this number, the search will be done using the HNSW index.
}

AUTH_USER_MODEL = 'catalogue.User'

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles')]
STATIC_ROOT =os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'catalogue.backends.CustomEmailBackend', 
]

# Settings for sending password reset email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER =  os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD =  os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# checking if the values are set in environtment
# if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
#     raise ValueError("""Email settings are not properly configured. 
#                      Make sure to set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD environment variables.""")