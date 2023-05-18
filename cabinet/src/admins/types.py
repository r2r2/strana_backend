from typing import NewType
from passlib import context
from common import messages, session, email


AdminSms = NewType("AdminSms", messages.SmsService)
AdminEmail = NewType("AdminEmail", email.EmailService)
AdminHasher = NewType("AdminHasher", context.CryptContext)
AdminSession = NewType("AdminSession", session.SessionStorage)
