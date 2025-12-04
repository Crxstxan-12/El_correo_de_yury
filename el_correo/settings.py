"""
Configuración de Django para el proyecto El Correo.

Incluye carga de variables de entorno, apps instaladas, middleware,
plantillas, conexión a base de datos MySQL y opciones de internacionalización.
Se comenta cada sección para facilitar mantenimiento y despliegue.

Referencias:
https://docs.djangoproject.com/en/5.2/topics/settings/
https://docs.djangoproject.com/en/5.2/ref/settings/
"""
import os
from pathlib import Path
from dotenv import load_dotenv
# Carga variables desde '.env' en el directorio del proyecto
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-+^5_qsd=l1fwhe%rq-9d=6tlf$fjs-7wdn*7#j+2tf8a1x%9kd')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Hosts permitidos para servir la app; en producción incluye dominio/IP
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',             # Seguridad general
    'django.contrib.sessions.middleware.SessionMiddleware',       # Manejo de sesiones
    'django.middleware.common.CommonMiddleware',                  # Funcionalidades comunes de Django
    'django.middleware.csrf.CsrfViewMiddleware',                  # Protección contra ataques CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',     # Autenticación de usuarios
    'django.contrib.messages.middleware.MessageMiddleware',        # Sistema de mensajes
    'django.middleware.clickjacking.XFrameOptionsMiddleware',      # Protección contra clickjacking
]


ROOT_URLCONF = 'el_correo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',  # opcional pero recomendado
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'el_correo.wsgi.application'


# Base de datos
# Usa MySQL con `pymysql` y variables de entorno:
# - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST (por defecto 'localhost'), DB_PORT (por defecto '3306')
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

import pymysql
pymysql.install_as_MySQLdb()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        # Activa modo estricto de MySQL para evitar datos inválidos
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Archivos estáticos (CSS, JS, imágenes)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Rutas de autenticación por defecto para Login/Logout/Redirect
# Rutas de autenticación por defecto para Login/Logout/Redirect
LOGIN_URL = '/usuarios/login/'
LOGIN_REDIRECT_URL = '/usuarios/dashboard/'
LOGOUT_REDIRECT_URL = '/usuarios/login/'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
