"""
Импорт фикстур
"""

# основные фикстуры
from .event_loop_fixtures import *
from .db_fixtures import *
from .app_fixtures import *
from .client_fixtures import *
from .faker_fixtures import *

# фикстуры приложений
from .common.sync_fixtures import *
from .users.repos_fixtures import *
from .users.sync_fixtures import *
from .users.async_fixtures import *
from .agencies.sync_fixtures import *
from .agencies.async_fixtures import *
from .properties.repos_fixtures import *
from .bookings.repos_fixtures import *
from .meetings.repos_fixtures import *
