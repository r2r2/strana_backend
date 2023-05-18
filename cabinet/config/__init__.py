import os
from pathlib import Path
from typing import Any

from config.settings import (AerichSettings, AMOCrmSettings,
                             ApplicationSettings, AuthSettings, AWSSettings,
                             BackendSettings, BazisSettings, BookingSettings,
                             CelerySettings, CORSSettings, DataBaseSettings,
                             EmailRecipientsSettings, EmailSettings, EnvTypes,
                             GetdocSettings, ImgproxySettings, LKAdminSettins,
                             MaintenanceSettings, ProfitbaseSettings,
                             RedisSettings, SberbankSettings, SentrySettings,
                             SessionSettings, SiteSettings, SmsCenterSettings,
                             TortoiseSettings, TrustedSettings, FakeSendSms,
                             UvicornSettings, LogsSettings, SenseiSettings,
                             KonturTalkSettings)


base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = Path(base_dir) / 'logs'
logs_dir.mkdir(exist_ok=True)


aws_config: dict[str, Any] = AWSSettings().dict()
cors_config: dict[str, Any] = CORSSettings().dict()
site_config: dict[str, Any] = SiteSettings().dict()
auth_config: dict[str, Any] = AuthSettings().dict()
redis_config: dict[str, Any] = RedisSettings().dict()
email_config: dict[str, Any] = EmailSettings().dict()
sentry_config: dict[str, Any] = SentrySettings().dict()
celery_config: dict[str, Any] = CelerySettings().dict()
amocrm_config: dict[str, Any] = AMOCrmSettings().dict()
booking_config: dict[str, Any] = BookingSettings().dict()
trusted_config: dict[str, Any] = TrustedSettings().dict()
backend_config: dict[str, Any] = BackendSettings().dict()
uvicorn_config: dict[str, Any] = UvicornSettings().dict()
session_config: dict[str, Any] = SessionSettings().dict()
imgproxy_config: dict[str, Any] = ImgproxySettings().dict()
sberbank_config: dict[str, Any] = SberbankSettings().dict()
database_config: dict[str, Any] = DataBaseSettings().dict()
sms_center_config: dict[str, Any] = SmsCenterSettings().dict()
profitbase_config: dict[str, Any] = ProfitbaseSettings().dict()
aerich_config: dict[str, Any] = AerichSettings.generate().dict()
application_config: dict[str, Any] = ApplicationSettings().dict()
tortoise_config: dict[str, Any] = TortoiseSettings.generate().dict()
aerich_test_config: dict[str, Any] = AerichSettings.generate(testing=True).dict()
tortoise_test_config: dict[str, Any] = TortoiseSettings.generate(testing=True).dict()
bazis_config: dict[str, Any] = BazisSettings().dict()
lk_admin_config: dict[str, Any] = LKAdminSettins().dict()
email_recipients_config: dict[str, Any] = EmailRecipientsSettings().dict()
maintenance_settings: dict[str, Any] = MaintenanceSettings().dict()
getdoc_settings: dict[str, Any] = GetdocSettings().dict()
fake_sms_send: dict[str, Any] = FakeSendSms().dict()
sensei_config: dict[str, Any] = SenseiSettings().dict()
kontur_talk_config: dict[str, Any] = KonturTalkSettings().dict()
logs_config: dict[str, Any] = LogsSettings().dict()
