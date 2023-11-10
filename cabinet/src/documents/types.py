from typing import NewType
from common import session, paginations


DocumentSession = NewType("DocumentSession", session.SessionStorage)
InteractionDocumentsPagination = NewType("AgencyPagination", paginations.PagePagination)
