from django.conf import settings

LOCATION_SOURCE_URL = getattr(settings, 'LOCATION_SOURCE_URL', 'http://ipgeobase.ru/files/db/Main/geo_files.zip')
LOCATION_CODING = getattr(settings, 'LOCATION_CODING', 'windows-1251')
LOCATION_SEND_MESSAGE_FOR_ERRORS = getattr(settings, 'LOCATION_SEND_MESSAGE_FOR_ERRORS', True)
