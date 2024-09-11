from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SETTINGS_PATH = BASE_DIR / "config.yml"

TESTS_FOLDER = BASE_DIR / "tests"
FIXTURES_FOLDER = BASE_DIR / "fixtures"
TESTS_DATA_FOLDER = TESTS_FOLDER / "data"
LUA_SCRIPTS_FOLDER = BASE_DIR / "src" / "core" / "common" / "redis" / "scripts"

INT32_MAX = 2_147_483_647
