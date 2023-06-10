#!/bin/bash

python manage.py collectstatic --noinput
python manage.py migrate

echo "Static files collected and database migrated"
