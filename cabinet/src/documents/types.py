from typing import NewType
from common import session


DocumentSession = NewType("DocumentSession", session.SessionStorage)
