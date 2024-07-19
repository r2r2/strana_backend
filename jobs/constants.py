from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

SETTINGS_PATH = BASE_DIR / "config" / "config.jobs.yml"

QUEUE_INTERNAL_NAME = "internal_liga_pro"

SENTRY_APP_NAME = "JOBS"
