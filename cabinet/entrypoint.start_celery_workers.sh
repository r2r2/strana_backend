#!/bin/sh


# Start the first Celery worker
celery -A config.celery worker -B -l info -n tasks@strana.com -Q tasks --autoscale=4,8 &

# Start the second Celery worker
#celery -A config.celery worker -B -l info -n periodic_tasks@strana.com -Q periodic_tasks --autoscale=4,8 &


wait
