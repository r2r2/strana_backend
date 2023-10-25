#pylint: disable=missing-function-docstring
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseSettings, Field, root_validator


class SiteSettings(BaseSettings):
    site_email: str = Field("booking@strana.com", env='LK_STRANA_BOOKING_EMAIL')
    main_site_host: str = Field("localhost", env="MAIN_SITE_HOST")
    site_host: str = Field("lk.localhost", env="LK_SITE_HOST")
    broker_site_host: str = Field("broker.localhost", env="BROKER_LK_SITE_HOST")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ApplicationSettings(BaseSettings):
    root_path: str = Field("/api")
    title: str = Field("Личный кабинет Страна девелопмент")

    debug: bool = Field(True, env="LK_DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class RequestLimiterSettings(BaseSettings):
    max_requests: float = Field(5, env="LK_MAX_REQUESTS")
    period: float = Field(1, env="LK_MAX_REQUESTS_PERIOD")  # in seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class UvicornSettings(BaseSettings):
    app: str = Field("config.asgi:application")

    port: int = Field(1800, env="LK_PORT")
    ws: str = Field("wsproto", env="LK_WS")
    reload: bool = Field(True, env="LK_RELOAD")
    host: str = Field("0.0.0.0", env="LK_HOST")
    log_level: str = Field("debug", env="LK_LOG_LEVEL")
    use_colors: bool = Field(True, env="LK_USE_COLORS")
    proxy_headers: bool = Field(True, env="LK_PROXY_HEADERS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class DataBaseSettings(BaseSettings):
    default_dsn: str = Field(
        "postgres://{user}:{password}@{host}:{port}/{database}?maxsize={maxsize}"
    )
    test_dsn: str = Field(
        "postgres://{user}:{password}@{host}:{port}/{database_test}?maxsize={maxsize}"
    )

    port: str = Field("5432", env="LK_POSTGRES_PORT")
    maxsize: str = Field("20", env="LK_POSTGRES_MAXSIZE")
    user: str = Field("postgres", env="LK_POSTGRES_USER")
    host: str = Field("db_cabinet", env="LK_POSTGRES_HOST")
    password: str = Field("postgres", env="LK_POSTGRES_PASSWORD")
    database: str = Field("postgres", env="LK_POSTGRES_DATABASE")
    database_test: str = Field("cabinet_test", env="LK_POSTGRES_DATABASE_TEST")
    test_user: str = Field("postgres", env="POSTGRES_USER_TEST")
    test_password: str = Field("postgres", env="POSTGRES_PASSWORD_TEST")
    test_host: str = Field("localhost", env="POSTGRES_HOST_TEST")
    test_port: str = Field("5432", env="POSTGRES_PORT_TEST")

    models: list[tuple] = [
        ("users", "repos"),
        ("properties", "repos"),
        ("documents", "repos"),
        ("payments", "repos"),
        ("projects", "repos"),
        ("buildings", "repos"),
        ("floors", "repos"),
        ("booking", "repos"),
        ("agencies", "repos"),
        ("agents", "repos"),
        ("tips", "repos"),
        ("pages", "repos"),
        ("notifications", "repos"),
        ("showtimes", "repos"),
        ("cities", "repos"),
        ("amocrm", "repos"),
        ("cautions", "repos"),
        ("getdoc", "repos"),
        ("agreements", "repos"),
        ("questionnaire", "repos"),
        ("task_management", "repos"),
        ("meetings", "repos"),
        ("text_blocks", "repos"),
        ("email", "repos"),
        ("messages", "repos"),
        ("events", "repos"),
        ("dashboard", "repos"),
        ("menu", "repos"),
        ("settings", "repos"),
        ("main_page", "repos"),
        ("additional_services", "repos"),
        ("events_list", "repos"),
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class BackendDataBaseSettings(BaseSettings):
    default_dsn: str = Field(
        "postgres://{user}:{password}@{host}:{port}/{database}?maxsize={maxsize}"
    )
    test_dsn: str = Field(
        "postgres://{user}:{password}@{host}:{port}/{database_test}?maxsize={maxsize}"
    )

    port: str = Field("5432", env="PORTAL_POSTGRES_PORT")
    maxsize: str = Field("20", env="POSTGRES_MAXSIZE")
    user: str = Field("postgres", env="PORTAL_POSTGRES_USER")
    host: str = Field("db_cabinet", env="PORTAL_POSTGRES_HOST")
    password: str = Field("postgres", env="PORTAL_POSTGRES_PASSWORD")
    database: str = Field("postgres", env="PORTAL_POSTGRES_DATABASE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AuthSettings(BaseSettings):
    type: str = Field("Bearer")
    password_time: int = Field(3)
    algorithm: str = Field("HS256")
    expires: int = Field(60 * 24 * 30)
    hasher_deprecated: str = Field("auto")
    hasher_schemes: list[str] = Field(["bcrypt"])

    secret_key: str = Field("secret_key", env="LK_AUTH_SECRET_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class BackendSettings(BaseSettings):
    db_host: str = Field("db", env="PORTAL_POSTGRES_HOST")
    db_port: str = Field("5432", env="PORTAL_POSTGRES_PORT")
    db_user: str = Field("postgres", env="PORTAL_POSTGRES_USER")
    db_name: str = Field("postgres", env="PORTAL_POSTGRES_DATABASE")
    db_password: str = Field("postgres", env="PORTAL_POSTGRES_PASSWORD")

    graphql: str = Field("/graphql/", env="LK_BACKEND_GRAPHQL")
    url: str = Field("https://stranadev-new.com", env="LK_BACKEND_URL")
    external_url: str = Field("https://stranadev-new.com", env="LK_EXTERNAL_BACKEND_URL")
    internal_login: str = Field("internal_login", env="INTERNAL_LOGIN")
    internal_password: str = Field("internal_password", env="INTERNAL_PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class MCSettings(BaseSettings):
    url: str = Field("https://services.stranadev-new.com/api", env="MC_BACKEND_URL")


class SberbankSettings(BaseSettings):
    secret: str = Field("FJbdau831yhb41dsSYDUvjg42", env="SBERBANK_SECRET")
    msk_username: str = Field("msk_username", env="SBERBANK_SPB_USERNAME")
    msk_password: str = Field("msk_password", env="SBERBANK_SPB_PASSWORD")
    spb_username: str = Field("spb_username", env="SBERBANK_SPB_USERNAME")
    spb_password: str = Field("spb_password", env="SBERBANK_SPB_PASSWORD")
    tmn_username: str = Field("tmn_username", env="SBERBANK_TMN_USERNAME")
    tmn_password: str = Field("tmn_password", env="SBERBANK_TMN_PASSWORD")
    ekb_username: str = Field("ekb_username", env="SBERBANK_SPB_USERNAME")
    ekb_password: str = Field("ekb_password", env="SBERBANK_SPB_PASSWORD")
    test_case_username: str = Field("test_case_username", env="TEST_CASE_USERNAME")
    test_case_password: str = Field("test_case_password", env="TEST_CASE_PASSWORD")
    url: str = Field("https://3dsec.sberbank.ru/payment/rest/", env="SBERBANK_URL")
    return_url: str = Field("/api/booking/sberbank/{}/{}", env="SBERBANK_RETURN_URL")
    frontend_return_url: str = Field("/booking", env="SBERBANK_FRONTEND_RETURN_URL")
    frontend_fast_return_url: str = Field("/fast-booking", env="SBERBANK_FRONTEND_FAST_RETURN_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class CelerySettings(BaseSettings):
    task_serializer: str = Field("json")
    result_serializer: str = Field("json")
    timezone: str = Field('Europe/Moscow')
    accept_content: list[str] = Field(["json"])
    broker_url: str = Field("redis://redis-lk-broker:6379/0", env='LK_BROKER_URL')
    result_backend: str = Field("redis://redis-lk-broker:6379/0", env='LK_RESULT_BACKEND')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AMOCrmSettingsOld(BaseSettings):
    api_route: str = Field("/api/v2")
    api_route_v4: str = Field("/api/v4")
    auth_route: str = Field("/oauth2/access_token")
    url: str = Field("https://eurobereg72.amocrm.ru")
    upload_url: str = Field("https://amocon.itstrana.site/amoconnector/widget_up_file")
    widget_aquire_url: str = Field("https://amocon.itstrana.site/amoconnector/widget_aquire")

    db_table: str = Field("amocrm_amocrmsettings")
    db_host: str = Field("db", env="PORTAL_POSTGRES_HOST")
    db_port: str = Field("5432", env="PORTAL_POSTGRES_PORT")
    db_user: str = Field("postgres", env="PORTAL_POSTGRES_USER")
    db_name: str = Field("postgres", env="PORTAL_POSTGRES_DATABASE")
    db_password: str = Field("postgres", env="PORTAL_POSTGRES_PASSWORD")
    secret: str = Field("HJFjasdhsgybh432dsaJHdasj", env="AMOCRM_SECRET")
    partition_limit: int = Field(50, env="AMOCRM_PARTITION_LIMIT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AMOCrmSettings(BaseSettings):
    api_route: str = Field("/api/v2")
    api_route_v4: str = Field("/api/v4")
    auth_route: str = Field("/oauth2/access_token")
    url: str = Field("https://eurobereg72.amocrm.ru")
    upload_url: str = Field("https://amocon.itstrana.site/amoconnector/widget_up_file")
    widget_aquire_url: str = Field("https://amocon.itstrana.site/amoconnector/widget_aquire")

    db_table: str = Field("amocrm_amocrm_settings")
    db_host: str = Field("db", env="LK_POSTGRES_HOST")
    db_port: str = Field("5432", env="LK_POSTGRES_PORT")
    db_user: str = Field("postgres", env="LK_POSTGRES_USER")
    db_name: str = Field("postgres", env="LK_POSTGRES_DATABASE")
    db_password: str = Field("postgres", env="LK_POSTGRES_PASSWORD")
    secret: str = Field("HJFjasdhsgybh432dsaJHdasj", env="AMOCRM_SECRET")
    partition_limit: int = Field(50, env="AMOCRM_PARTITION_LIMIT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class SenseiSettings(BaseSettings):
    url: str = Field("https://api.sensei.plus")
    api_route: str = Field("/v1/")

    secret: str = Field("secret", env="SENSEI_SECRET")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class KonturTalkSettings(BaseSettings):
    space: str = Field("space", env="KONTUR_TALK_SPACE")
    secret: str = Field("secret", env="KONTUR_TALK_SECRET")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ProfitbaseSettings(BaseSettings):
    auth_route: str = Field("/authentication")

    api_key: str = Field("api_key", env="LK_PROFITBASE_API_KEY")
    url: str = Field("https://pb4988.profitbase.ru/api/v4/json", env="PROFITBASE_BASE_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class SmsCenterSettings(BaseSettings):
    login: str = Field("login", env="SMS_CENTER_LOGIN")
    password: str = Field("password", env="SMS_CENTER_PASSWORD")
    url: str = Field("https://smsc.ru/sys/send.php", env="SMS_CENTER_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class SentrySettings(BaseSettings):
    dsn: str = Field("https://dsn.ru", env="LK_SENTRY_DSN")
    send_default_pii: bool = Field(True)  # personally identifiable information (PII)
    max_value_length: int = Field(8192)   # DEFAULT_MAX_VALUE_LENGTH = 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class CORSSettings(BaseSettings):
    allow_credentials: bool = Field(True)
    allow_methods: list[str] = Field(["*"])
    allow_headers: list[str] = Field(["*", "Authorization"])
    allow_origins: list[str] = Field(["*"], env="CORS_ORIGINS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class TrustedSettings(BaseSettings):
    allowed_hosts: list[str] = Field(["*"])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class RedisSettings(BaseSettings):
    address: str = Field("redis://redis-lk-broker:6379/13", env='LK_REDDIS_URL')
    host: str = Field("redis-lk-broker", env='LK_REDIS_HOST')
    port: int = Field(6379, env='LK_REDIS_PORT')
    db: int = Field(13, env='LK_REDIS_DB')

    deleted_users_key: str = Field("deleted_users")
    deleted_users_expire: int = Field(2_147_483_647)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class SessionSettings(BaseSettings):
    len: int = Field(64)
    cookie_len: int = Field(86)
    key: str = Field("_lksession")
    expire: int = Field(3_000_000)
    auth_attempts_expire: int = Field(600)
    session_timeout: int = Field(20 * 60)
    last_activity_key: str = Field("last_activity_timestamp")

    domain: str = Field("lk.localhost", env="LK_SESSION_DOMAIN")
    amocrm_exclusion: str = Field("HJFjasdhsgybh432dsaJHdasj", env="AMOCRM_SECRET")

    auth_key: str = Field("auth_info")
    auth_attempts_key: str = Field("auth_attempts")
    document_key: str = Field("document_info")
    password_reset_key: str = Field("reset_info")
    password_settable_key: str = Field("set_info")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class BookingDevSettings(BaseSettings):
    period_days: Union[int, float] = Field(1/96)
    time_minutes: int = Field(15)
    time_seconds: int = Field(900)
    time_hours: float = Field(0.25)
    fast_time_hours: float = Field(0.25)


class BookingSettings(BaseSettings):
    period_days: int = Field(20)
    time_minutes: int = Field(20)
    time_seconds: int = Field(1200)
    time_hours: Union[int, float] = Field(24)
    fast_time_hours: int = Field(24)

    @root_validator
    def set_dev_time(cls, values: dict):
        if MaintenanceSettings().environment in [EnvTypes.DEV, EnvTypes.STAGE]:
            values["time_minutes"] = BookingDevSettings().time_minutes
            values["time_seconds"] = BookingDevSettings().time_seconds
            values["time_hours"] = BookingDevSettings().time_hours
            values["fast_time_hours"] = BookingDevSettings().fast_time_hours
        return values

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class EmailSettings(BaseSettings):
    port: int = Field(587)
    use_tls: bool = Field(True)
    use_ssl: bool = Field(False)
    use_cred: bool = Field(True)
    sender_name: str = Field("Страна Девелопмент")

    host: str = Field("server", env="EMAIL_HOST")
    sender: str = Field("sender", env="EMAIL_HOST_USER")
    username: str = Field("username", env="EMAIL_HOST_USER")
    password: str = Field("password", env="EMAIL_HOST_PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class TortoiseSettings(BaseSettings):
    generate_schemas: Optional[bool]
    apps: Optional[dict[str, Any]]
    connections: Optional[dict[str, Any]]
    routers: Optional[list[str]]

    @classmethod
    def generate(cls, testing=False):

        database = DataBaseSettings()
        backend_database = BackendDataBaseSettings()
        connections: Optional[dict[str, Any]]
        apps: Optional[dict[str, Any]]
        routers: Optional[list[str]] = ['config.routers.DBRouter']
        if testing:
            modules = ["aerich.models"]
            for model in database.models:
                if model[0] not in ("email", "messages", "settings"):
                    modules.append(f"src.{model[0]}.{model[1]}")
                else:
                    modules.append(f"common.{model[0]}.{model[1]}")

            connections = {
                "cabinet": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": database.database_test,
                        "host": database.test_host,
                        "password": database.test_password,
                        "port": database.test_port,
                        "user": database.test_user,
                    },
                },
            }
            apps = {
                "models": {
                    "models": modules,
                    "default_connection": "cabinet",
                },
            }
        else:
            modules = []
            for model in database.models:
                if model[0] not in ("email", "messages", "settings"):
                    modules.append(f"src.{model[0]}.{model[1]}")
                else:
                    modules.append(f"common.{model[0]}.{model[1]}")

            connections = {
                "cabinet": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": database.database,
                        "host": database.host,
                        "password": database.password,
                        "port": database.port,
                        "user": database.user,
                    },
                },
                "backend": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": backend_database.database,
                        "host": backend_database.host,
                        "password": backend_database.password,
                        "port": backend_database.port,
                        "user": backend_database.user,
                    },
                },
            }
            apps = {
                "models": {
                    "models": modules,
                    "default_connection": "cabinet",
                },
                "backend": {
                    "models": ["common.backend.models"],
                    "default_connection": "backend",
                },
            }
        print(connections)
        return cls(
            apps=apps,
            connections=connections,
            generate_schemas=False,
            routers=routers,
        )


class AerichSettings(BaseSettings):
    apps: dict
    connections: dict

    @classmethod
    def generate(cls, testing=False):
        database = DataBaseSettings()
        if testing:
            db_url = database.test_dsn.format(**database.dict())
        else:
            db_url = database.default_dsn.format(**database.dict())
        connections = dict(default=db_url)
        apps = dict(models=dict(models=["aerich.models"]))
        for model in database.models:
            if model[0] not in ("email", "messages", "settings"):
                apps["models"]["models"].append(f"src.{model[0]}.{model[1]}")
            else:
                apps["models"]["models"].append(f"common.{model[0]}.{model[1]}")
        return cls(connections=connections, apps=apps)


class AWSSettings(BaseSettings):
    access_key_id: str = Field("server", env="AWS_ACCESS_KEY_ID")
    secret_access_key: str = Field("server", env="AWS_SECRET_ACCESS_KEY")
    storage_bucket_name: str = Field("server", env="AWS_STORAGE_BUCKET_NAME")
    endpoint_url: str = Field("server", env="AWS_S3_ENDPOINT_URL")
    custom_domain: str = Field("server", env="AWS_S3_CUSTOM_DOMAIN_LK")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ImgproxySettings(BaseSettings):
    key: str = Field("key", env="IMGPROXY_KEY")
    salt: str = Field("salt", env="IMGPROXY_SALT")
    s3_endpoint: str = Field("s3_endpoint", env="IMGPROXY_S3_ENDPOINT")
    site_host: str = Field("imgproxy.localhost", env="IMGPROXY_SITE_HOST")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class BazisSettings(BaseSettings):
    url: str = Field("server", env="BAZIS_URL")
    username: str = Field("username", env="BAZIS_USERNAME")
    password: str = Field("password", env="BAZIS_PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class LKAdminSettins(BaseSettings):
    url: str = Field('lk.localhost', env='LK_SITE_HOST')
    token: str = Field('artw:artw123', env='LK_ADMIN_TOKEN')
    admin_export_key: str = Field('default_key', env='EXPORT_CABINET_KEY')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class EmailRecipientsSettings(BaseSettings):
    strana_manager: list = Field(['makarova@artw.ru'], env='LK_STRANA_MANAGER_EMAIL')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class EnvTypes(str, Enum):
    DEV = "dev"
    PROD = "prod"
    STAGE = "stage"


class MaintenanceSettings(BaseSettings):
    environment: EnvTypes = Field('prod', env='LK_STRANA_ENVIRONMENT')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class GetdocSettings(BaseSettings):
    url: str = Field("https://v2.widget8.ru/getdoc/templates/generate", env='LK_STRANA_GETDOC_URL')

    amo_domain: str = Field('amorcm', env='LK_STRANA_GETDOC_AMO_DOMAIN')
    account_id: int = Field(0, env='LK_STRANA_GETDOC_ACCOUNT_ID')
    user_id: int = Field(0, env='LK_STRANA_GETDOC_USER_ID')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class FakeSendSms(BaseSettings):
    numbers: list[str] = Field(["+79999999999"], env="LK_STRANA_FAKE_NUMBERS")
    code: str = Field("9999", env='LK_STRANA_FAKE_SMS_CODE')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class LogsSettings(BaseSettings):
    logs_lifetime: int = Field(3, env="LOGS_LIFETIME")
    logs_notification_lifetime: int = Field(14, env="LOGS_NOTIFICATION_LIFETIME")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class UnleashSettings(BaseSettings):
    url: str = Field("", env="LK_UNLEASH_URL")
    instance_id: str = Field("", env="LK_UNLEASH_INSTANCE_ID")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class DepregSettings(BaseSettings):
    """
    Настройки для работы с API Depreg.
    """
    base_url: str = Field("https://et.depreg.ru/api/v2", env="LK_DEPREG_BASE_URL")
    auth_type: str = Field("Bearer", env="LK_DEPREG_AUTH_TYPE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
