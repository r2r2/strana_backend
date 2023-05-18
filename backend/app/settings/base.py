"""
   _____ _                                    _   _   _
  / ____| |                                  | | | | (_)
 | (___ | |_ _ __ __ _ _ __   __ _   ___  ___| |_| |_ _ _ __   __ _ ___
  \___ \| __| '__/ _` | '_ \ / _` | / __|/ _ \ __| __| | '_ \ / _` / __|
  ____) | |_| | | (_| | | | | (_| | \__ \  __/ |_| |_| | | | | (_| \__ \
 |_____/ \__|_|  \__,_|_| |_|\__,_| |___/\___|\__|\__|_|_| |_|\__, |___/
                                                               __/ |
                                                              |___/
"""
import json
#trigg ci
import os
import sys
import unittest
from distutils.util import strtobool

import faker.config
from django.utils.translation import gettext_lazy as _

from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv("SECRET_KEY", "rw+t6fn87n-r+9%$s^r8hvja2yux(rz#!8th3_1^e2^z-9!3!l")

TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

DEBUG = os.getenv("DEBUG", "True") == "True" and not TESTING

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
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
    "drf_spectacular",
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
    "import_export",
]

if DEBUG:
    INSTALLED_APPS.extend(("debug_toolbar",))
    INSTALLED_APPS.append("graphiql_debug_toolbar")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
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

if os.getenv("REQUESTS_FULL_LOGGING", False):
    MIDDLEWARE.append("common.middleware.APIRequestMiddleware")

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


DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": "app.settings.show_toolbar_callback"}

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
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_TIMEZONE = "Europe/Moscow"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERYBEAT_SCHEDULE = {
    "update_credentials": {
        "task": "amocrm.tasks.update_credentials",
        "schedule": crontab(minute="*/10"),
    },
    "update_projects_task": {
        "task": "profitbase.tasks.update_projects_task",
        "schedule": crontab(minute="*/20"),
    },
    "update_buildings_task": {
        "task": "profitbase.tasks.update_buildings_task",
        "schedule": crontab(minute="*/20"),
    },
    "update_offers_task": {
        "task": "profitbase.tasks.update_offers_task",
        "schedule": crontab(minute="*/20"),
    },
    "notify_realty_update_managers_task": {
        "task": "profitbase.tasks.notify_realty_update_managers_task",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "vk_update_or_create_posts": {
        "task": "vk.tasks.scraping_posts_vk",
        "schedule": crontab(minute=10, hour="*/6"),
    },
    "calculate_city_fields_task": {
        "task": "cities.tasks.calculate_city_fields_task",
        "schedule": crontab(minute="*/30"),
    },
    "calculate_project_fields_task": {
        "task": "projects.tasks.calculate_project_fields_task",
        "schedule": crontab(minute="*/30"),
    },
    "calculate_building_fields_task": {
        "task": "buildings.tasks.calculate_building_fields_task",
        "schedule": crontab(minute="*/30"),
    },
    "calculate_section_fields_task": {
        "task": "buildings.tasks.calculate_section_fields_task",
        "schedule": crontab(minute="*/30"),
    },
    "calculate_floor_fields_task": {
        "task": "buildings.tasks.calculate_floor_fields_task",
        "schedule": crontab(minute="*/30"),
    },
    "calculate_mortgage_page_fields_task": {
        "task": "mortgage.tasks.calculate_mortgage_page_fields_task",
        "schedule": crontab(minute="*/30"),
    },
    "calculate_current_level_task": {
        "task": "buildings.tasks.calculate_current_level_task",
        "schedule": crontab(minute=0, hour="9"),
    },
    "notify_start_auction_task": {
        "task": "auction.tasks.notify_start_auction_task",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "deactivate_old_actions_task": {
        "task": "news.tasks.deactivate_old_actions_task",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "update_layouts_task": {
        "task": "properties.tasks.update_layouts_task",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "update_layouts_facing_by_property_task": {
        "task": "properties.tasks.update_layouts_facing_by_property_task",
        "schedule": crontab(minute=0, hour="*/1")
    },
    "deactivate_main_page_slides_task": {
        "task": "main_page.tasks.deactivate_main_page_slides_task",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "update_special_offers_activity_task": {
        "task": "properties.tasks.update_special_offers_activity_task",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "send_callback_amo": {
        "task": "request_forms.tasks.send_amo_lead_callback_request",
        "schedule": crontab(minute=0, hour="9,11,13,15,19"),
    },
    "update_offers_data_task": {
        "task": "dvizh_api.tasks.update_offers_data_task",
        "schedule": crontab(minute=0, hour="*/1"),
    },
}

# Sentry
if "SENTRY_DSN" in os.environ:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"], integrations=[DjangoIntegration(), CeleryIntegration()]
    )


# Session
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN", None)
SESSION_CACHE_ALIAS = "sessions"

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

# Profitbase
PROFITBASE_BASE_URL = os.environ.get("PROFITBASE_BASE_URL")
PROFITBASE_API_KEY = os.environ.get("PROFITBASE_API_KEY")

# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "profitbase": {"()": "logging.Formatter", "format": "[{asctime}] {message}", "style": "{"}
    },
    "handlers": {
        "console": {"level": "INFO", "formatter": "profitbase", "class": "logging.StreamHandler"}
    },
    "loggers": {"profitbase": {"handlers": ["console"], "level": "INFO", "propagate": False}},
}

# Graphene
GRAPHENE = {
    "SCHEMA": "app.schema.schema",
    "SCHEMA_OUTPUT": "schema.json",
    "MIDDLEWARE": ["graphene_django.debug.DjangoDebugMiddleware"],
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

# Redirect
DEFAULT_SITE_URL_REDIRECT = os.getenv("DEFAULT_SITE_HOST_REDIRECT", "https://tmn.strana.com")

# Internal auth
INTERNAL_LOGIN = os.getenv("INTERNAL_LOGIN")
INTERNAL_PASSWORD = os.getenv("INTERNAL_PASSWORD")

# CORS
CORS_ALLOWED_ORIGINS = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost"]'))
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

IMGPROXY_KEY = os.getenv("IMGPROXY_KEY")
IMGPROXY_SALT = os.getenv("IMGPROXY_SALT")
IMGPROXY_SITE_HOST = os.getenv("IMGPROXY_SITE_HOST")

# Django Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


VK_TOKEN = os.getenv("VK_TOKEN")

SPECTACULAR_SETTINGS = {
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/panel/",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
    "SERVE_AUTHENTICATION": ["rest_framework.authentication.BasicAuthentication"]
}

API_LOGGING_SETTINGS = {
    "LOGGING_ENABLED": strtobool(os.getenv("REQUESTS_FULL_LOGGING", "False")),
    "SKIP_URL_NAMESPACES": ["admin", "djdt", "static"],
    "SKIP_URL_NAMES": [],
    "BATCH_SIZE": 20,
    "EXCLUDE_SENSITIVE_DATA": ["password", "token", "access", "refresh"]
}

CACHE_MIDDLEWARE_SECONDS = int(os.getenv("CACHE_TTL", 3600)) if not TESTING else 0
CACHE_MIDDLEWARE_KEY_PREFIX = f"django-cache-{SITE_HOST}"

# Cache
CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache", "LOCATION": os.getenv("REDIS_CACHE_URL", "redis://redis:6379/1"),
        "OPTIONS": {
            "TIMEOUT": CACHE_MIDDLEWARE_SECONDS,
            "KEY_PREFIX": f"django-cache-{SITE_HOST}"
        }
    },
    "sessions": {
        "BACKEND": "redis_cache.RedisCache", "LOCATION": os.getenv("SESSION_CACHE_URL", "redis://redis:6379/2")
    }
}

DADATA = {
    "TOKEN": os.getenv("DADATA_TOKEN"),
    "SECRET": os.getenv("DADATA_SECRET")
}
