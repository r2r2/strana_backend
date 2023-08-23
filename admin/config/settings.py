# pylint: disable=abstract-class-instantiated

import json
import os
import sys
from pathlib import Path

from django.utils.translation import gettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv("LK_SECRET_KEY", "rw+t6fn87n-r+9%$s^rfsdjfaa2yux(rz#!8th3_1^e2^z-9!3!l")

TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

DEBUG = "True"

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "grappelli",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.forms",
    "adminsortable2",
    "django_admin_listfilter_dropdown",
    "ajaximage",
    "ckeditor",
    "ckeditor_uploader",
    "imagekit",
    "phonenumber_field",
    "colorful",
    "nested_admin",
    "references.apps.ReferencesAppConfig",
    "users.apps.UsersAppConfig",
    "booking.apps.BookingAppConfig",
    "properties.apps.PropertiesAppConfig",
    "artefacts.apps.ArtefactsAppConfig",
    "documents.apps.DocumentsAppConfig",
    "log_viewer",
    "managers.apps.ManagersAppConfig",
    "disputes.apps.DisputesAppConfig",
    "contents.apps.ContentsAppConfig",
    "questionnaire.apps.QuestionnaireAppConfig",
    "task_management.apps.TaskManagementAppConfig",
    "admincharts",
    "notifications.apps.NotificationsAppConfig",
    "events.apps.EventAppConfig",
    "dashboard.apps.DashboardAppConfig",
    "settings.apps.SettingsAppConfig",
    "main_page.apps.MainPageAppConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [BASE_DIR],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request"
            ]
        },
    }
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASE_ROUTERS = ["config.routers.DatabaseRouter"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("PORTAL_POSTGRES_DATABASE"),
        "USER": os.getenv("PORTAL_POSTGRES_USER"),
        "PASSWORD": os.getenv("PORTAL_POSTGRES_PASSWORD"),
        "HOST": os.getenv("PORTAL_POSTGRES_HOST"),
        "PORT": os.getenv("PORTAL_POSTGRES_PORT"),
        "CONN_MAX_AGE": 600,
    },
    "lk": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("LK_POSTGRES_DATABASE"),
        "USER": os.getenv("LK_POSTGRES_USER"),
        "PASSWORD": os.getenv("LK_POSTGRES_PASSWORD"),
        "HOST": os.getenv("LK_POSTGRES_HOST"),
        "PORT": os.getenv("LK_POSTGRES_PORT"),
        "CONN_MAX_AGE": 600,
    },
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "ru"
LANGUAGES = (("ru", _("Russian")), ("en", _("English")))
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files
STATIC_URL = "/s/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# HTTP
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Media
MEDIA_URL = "/m/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
DEFAULT_FILE_STORAGE = "common.storages.HashedFilenameS3Boto3Storage"
BASE_FILE_STORAGE = "common.storages.CustomS3Boto3Storage"

FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_PERMISSIONS = 0o644

# Django Storages
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN")
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = None


if "SENTRY_DSN" in os.environ:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], integrations=[DjangoIntegration()])

# CKEditor
CKEDITOR_UPLOAD_PATH = "u/"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar_Custom": [
            {"name": "document", "items": ["Source"]},
            {
                "name": "clipboard",
                "items": [
                    "Cut",
                    "Copy",
                    "Paste",
                    "PasteText",
                    "PasteFromWord",
                    "-",
                    "Undo",
                    "Redo",
                ],
            },
            {
                "name": "paragraph",
                "items": [
                    "NumberedList",
                    "BulletedList",
                    "-",
                    "Outdent",
                    "Indent",
                    "-",
                    "Blockquote",
                    "-",
                    "JustifyLeft",
                    "JustifyCenter",
                    "JustifyRight",
                    "JustifyBlock",
                ],
            },
            {"name": "links", "items": ["Link", "Unlink", "Anchor"]},
            {"name": "insert", "items": ["Table", "HorizontalRule", "SpecialChar"]},
            "/",
            {"name": "styles", "items": ["Styles", "Format", "Font", "FontSize"]},
            {
                "name": "basicstyles",
                "items": [
                    "Bold",
                    "Italic",
                    "Underline",
                    "Strike",
                    "Subscript",
                    "Superscript",
                    "-",
                    "RemoveFormat",
                ],
            },
            {"name": "colors", "items": ["TextColor", "BGColor"]},
        ],
        "toolbar": "Custom",
        "extraPlugins": ["liststyle"],
    }
}

# Cache
if not TESTING:
    CACHES = {"default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis-lk-broker:6379")}
    }

# Session
if not DEBUG:
    # SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_COOKIE_AGE = 31_536_000
    SESSION_COOKIE_DOMAIN = os.getenv("LK_SESSION_DOMAIN", None)

# Imagekit
IMAGEKIT_CACHEFILE_DIR = "c"
IMAGEKIT_DEFAULT_FILE_STORAGE = BASE_FILE_STORAGE
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = "imagekit.cachefiles.strategies.Optimistic"

# App settings
SITE_HOST = os.getenv("LK_SITE_HOST")


# Internal auth
INTERNAL_LOGIN = os.getenv("INTERNAL_LOGIN")
INTERNAL_PASSWORD = os.getenv("INTERNAL_PASSWORD")

# CORS
CORS_ALLOWED_ORIGINS = json.loads(os.getenv("CORS_ORIGINS", "['http://localhost']"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

LOG_VIEWER_FILES = ['*']
LOG_VIEWER_FILES_PATTERN = '*.log*'
LOG_VIEWER_PAGE_LENGTH = 25       # total log lines per-page
LOG_VIEWER_MAX_READ_LINES = 1000  # total log lines will be read
LOG_VIEWER_FILE_LIST_MAX_ITEMS_PER_PAGE = 25  # Max log files loaded in Datatable per page
LOG_VIEWER_PATTERNS = ['=' * 60]
LOG_VIEWER_EXCLUDE_TEXT_PATTERN = None  # String regex expression to exclude the log from line
LOG_VIEWER_FILES_DIR = Path(BASE_DIR) / 'logs'
LOG_VIEWER_FILES_DIR.mkdir(exist_ok=True)

# Optionally you can set the next variables in order to customize the admin:
LOG_VIEWER_FILE_LIST_TITLE = "Логи ЛК"

LOGIN_URL = '/admin/login'

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)
