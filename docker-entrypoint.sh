#!/bin/sh

echo "Waiting for database..."
while ! nc -z ${DB_HOST} ${DB_PORT}; do sleep 1; done
echo "Connected to database."

python manage.py migrate --noinput
if [ $? -ne 0 ]; then
    echo "Migration failed." >&2
    exit 1
fi

echo "Starting Server..."
exec python manage.py runserver 0.0.0.0:8000
