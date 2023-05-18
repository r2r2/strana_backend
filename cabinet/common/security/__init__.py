from fastapi.security import OAuth2PasswordBearer
from .hashing import get_hasher
from .tokens import create_access_token, decode_access_token, create_email_token, decode_email_token

oauth2_scheme = OAuth2PasswordBearer("users/validate")
