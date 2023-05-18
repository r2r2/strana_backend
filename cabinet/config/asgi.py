from config.app import get_fastapi_application
from fastapi import FastAPI

application: FastAPI = get_fastapi_application()
