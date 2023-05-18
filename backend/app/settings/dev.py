import os

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

from common.utils import GraphQLLogFilter

load_dotenv(os.path.join(os.path.abspath(os.pardir), '.env'))

from .base import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv("SECRET_KEY", "rw+t6fn87n-r+9%$s^r8hvja2yux(rz#!8th3_1^e2^z-9!3!l")


DEBUG = True
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    # "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",

    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.forms",
    "django_filters",
    "solo",
    "adminsortable2",
    "django_admin_listfilter_dropdown",
    "ajaximage",
    "ckeditor",
    "ckeditor_uploader",
    "djcelery_email",
    "imagekit",
    "rangefilter",
    "phonenumber_field",
    "graphene_django",

    "colorful",
    "robots",
    "nested_admin",
    "corsheaders",
    "django_extensions",
    "rest_framework",
    "rest_framework_tracking",
    "rest_framework.authtoken",
    "drf_spectacular",
    "import_export",
    "profitbase.apps.ProfitBaseAppConfig",
    "users.apps.UsersAppConfig",
    "cities.apps.CitiesAppConfig",
    "projects.apps.ProjectsAppConfig",
    "buildings.apps.BuildingsAppConfig",
    "properties.apps.PropertiesAppConfig",
    "company.apps.CompanyAppConfig",
    "instagram.apps.InstagramAppConfig",
    "common.apps.CommonAppConfig",
    "news.apps.NewsAppConfig",
    "purchase.apps.PurchaseAppConfig",
    "contacts.apps.ContactsAppConfig",
    "main_page.apps.MainPageAppConfig",
    "infras.apps.InfrasAppConfig",
    "request_forms.apps.RequestFormsAppConfig",
    "commercial_property_page.apps.CommercialPropertyPageAppConfig",
    "commercial_project_page.apps.CommercialProjectPageConfig",
    "mortgage.apps.MortgageAppConfig",
    "amocrm.apps.AmoCRMAppConfig",
    "sitemap.apps.SitemapAppConfig",
    "location.apps.LocationAppConfig",
    "caches.apps.CachesAppConfig",
    "feeds.apps.FeedsConfig",
    "auction.apps.AuctionConfig",
    "landing.apps.LandingConfig",
    "panel_manager.apps.PanelManagerConfig",
    "dvizh_api.apps.DvizhApiConfig",
    "pop_ups.apps.PopUpsConfig",
    "investments.apps.InvestmentsConfig",
    "landowners.apps.LandownersConfig",
    "vk.apps.VkConfig",
    "vacancy.apps.VacancyConfig",
    "experiments.apps.ExperimentsConfig",

]

if DEBUG:
    INSTALLED_APPS.extend(("debug_toolbar",))
    INSTALLED_APPS.append("graphiql_debug_toolbar")

MIDDLEWARE = [
    # 'graphene_django.debug.DjangoDebugMiddleware',
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
    "favorite.middleware.FavoriteMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "common.middleware.APIRequestMiddleware",
]


if DEBUG:
    MIDDLEWARE.insert(0, "graphiql_debug_toolbar.middleware.DebugToolbarMiddleware")
    MIDDLEWARE.insert(1, "common.middleware.NonHtmlDebugToolbarMiddleware")

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.history.HistoryPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
    # 'pympler.panels.MemoryPanel',
]

DEBUG_TOOLBAR_CONFIG = {
    # Toolbar options
    'RESULTS_CACHE_SIZE': 3,
    'SHOW_COLLAPSED': True,
    'PROFILER_MAX_DEPTH': 30,
    'HIDE_IN_STACKTRACES': (
        "socketserver",
        "threading",
        "wsgiref",
        "debug_toolbar",
        'graphene_django.debug',
        'favorite',
        "django.db",
        "django.core.handlers",
        "django.core.servers",
        "django.utils.decorators",
        "django.utils.deprecation",
        "django.utils.functional",
    )

}



ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "app.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_NAME"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
        "CONN_MAX_AGE": 600,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "users.User"

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
if TESTING:
    DEFAULT_FILE_STORAGE = "django_hashedfilenamestorage.storage.HashedFilenameFileSystemStorage"
    BASE_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
else:
    DEFAULT_FILE_STORAGE = "common.storages.HashedFilenameS3Boto3Storage"
    BASE_FILE_STORAGE = "common.storages.CustomS3Boto3Storage"

FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_PERMISSIONS = 0o644

# Debug Toolbar
def show_toolbar_callback(_):
    return DEBUG


# DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": "app.settings.show_toolbar_callback"}

# Django Storages
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = None

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

# Email
EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_SUBJECT_PREFIX = "UniCredit: "
SERVER_EMAIL = EMAIL_HOST_USER

# Celery
# Add each celerybeat task to app.conf.task_routes in .celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
CELERY_TIMEZONE = "Europe/Moscow"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Imagekit
IMAGEKIT_CACHEFILE_DIR = "c"
IMAGEKIT_DEFAULT_FILE_STORAGE = BASE_FILE_STORAGE
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = "imagekit.cachefiles.strategies.Optimistic"

# Faker
faker.config.DEFAULT_LOCALE = "ru_RU"
# import common.faker_providers

# Unittest
# noinspection PyUnresolvedReferences
unittest.util._MAX_LENGTH = 15000

# App settings
SITE_HOST = os.getenv("SITE_HOST")
CRM_URL = os.getenv("CRM_URL")

# Profitbase
PROFITBASE_BASE_URL = os.environ.get("PROFITBASE_BASE_URL")
PROFITBASE_API_KEY = os.environ.get("PROFITBASE_API_KEY")

# Logging

# Graphene
GRAPHENE = {
    "SCHEMA": "app.schema.schema",
    "SCHEMA_OUTPUT": "schema.json",
    # "MIDDLEWARE": ["graphene_django.debug.DjangoDebugMiddleware"],
}

import common.converters

# Site for testing
if TESTING:
    SITE_ID = 1


# Robots
ROBOTS_USE_HOST = True
ROBOTS_USE_SITEMAP = True
ROBOTS_CACHE_TIMEOUT = None
ROBOTS_SITE_BY_REQUEST = True
ROBOTS_SITEMAP_VIEW_NAME = "sitemap"


DEFAULT_SITE_URL_REDIRECT = "http://127.0.0.1/"
INTERNAL_IPS = ['127.0.0.1', 'localhost']
# Internal auth
INTERNAL_LOGIN = os.getenv("INTERNAL_LOGIN")
INTERNAL_PASSWORD = os.getenv("INTERNAL_PASSWORD")


DATA_UPLOAD_MAX_NUMBER_FIELDS = None

IMGPROXY_KEY = os.getenv("IMGPROXY_KEY")
IMGPROXY_SALT = os.getenv("IMGPROXY_SALT")
IMGPROXY_SITE_HOST = os.getenv("IMGPROXY_SITE_HOST")
# Django Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        # "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

#VK
VK_TOKEN = os.getenv("VK_TOKEN")

SPECTACULAR_SETTINGS = {
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/panel/",
    # "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
    # "SERVE_AUTHENTICATION": ["rest_framework.authentication.BasicAuthentication"]
}
import logging

# l = logging.getLogger('django.db.backends')
# l.setLevel(logging.DEBUG)
# l.addHandler(logging.StreamHandler())
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "profitbase": {"()": "logging.Formatter", "format": "[{asctime}] {message}", "style": "{"},
        'simple': {
            'format': '[%(asctime)s] %(levelname)s | %(funcName)s | %(name)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'sample': {
            'format': 'velname)s %(message)s'
        },
    },
    "handlers": {
        "console": {"level": "DEBUG", "formatter": "profitbase", "class": "logging.StreamHandler"},
        'logger': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.dirname(os.path.dirname(BASE_DIR)) + '/logs/strana-backend.log',
            'formatter': 'simple',
        },
        "logstash": {
            "level": 'INFO',
            'class': 'logstash.TCPLogstashHandler',
            'formatter': 'simple',
            'host': 'localhost',
            'port': 5000,
            'version': 1,
            'message_type': 'django',
            'fqdn': False,
            'tags': ['django']
        }
    },
    "loggers": {
        # "profitbase": {"handlers": ["console"], "level": "INFO", "propagate": False},
        'django': {
            'handlers': ['logger', 'console'],
            'level': 'INFO', 'propagate': False
        },
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'handlers': ['logger',], 'propagate': False
        # },
        'graphql.execution.utils': {
            'level': 'INFO',
            'handlers': ['console']
        }
    },
}



API_LOGGING_SETTINGS = {
    "LOGGING_ENABLED": False,
    'SKIP_URL_NAMESPACES': ['admin', 'djdt', 'static'],
    'SKIP_URL_NAMES': [],
    'BATCH_SIZE': 5,
    'EXCLUDE_SENSITIVE_DATA': ['password', 'token', 'access', 'refresh']
}


# Cache
if not TESTING:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache"
        }
    }

CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = f"django-cache-{SITE_HOST}"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "profitbase": {"()": "logging.Formatter", "format": "[{asctime}] {message}", "style": "{"},
        'verbose': {
            'format': '[contactor] %(levelname)s %(asctime)s %(message)s'
        },
    },
    'filters': {
        'graphql_log_filter': {
            '()': GraphQLLogFilter,
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    "handlers": {
        "console": {"level": "INFO", "class": "logging.StreamHandler", 'filters': ['require_debug_false']},
    },

    "loggers": {
        'django': {
            'handlers': ['console', ],
            'level': 'INFO',
        },
        "profitbase": {"handlers": ["console", ], "level": "INFO", "propagate": False},
        'graphql.execution.utils': {
            'level': 'INFO',
            'handlers': ['console'],
            "class": "logging.StreamHandler",
            'filters': ['graphql_log_filter'],
            "propagate": False
        },
    },
}

SPECTACULAR_SETTINGS = {
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/panel/',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    # 'SERVE_AUTHENTICATION': ['rest_framework.authentication.BasicAuthentication']
}