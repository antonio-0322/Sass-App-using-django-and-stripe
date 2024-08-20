#!/bin/bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py seed_plans
python manage.py sync_plans
uvicorn config.asgi:application --host 0.0.0.0 --port 8100
