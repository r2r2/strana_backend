#!/bin/sh
python manage.py collectstatic --noinput
python manage.py compilemessages
exec "$@"