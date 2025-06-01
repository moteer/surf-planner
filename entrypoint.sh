#!/bin/sh

echo "⏳ Waiting for DB to be ready..."
until nc -z -v -w30 db 3306
do
  echo "Waiting for MySQL at db:3306..."
  sleep 1
done

echo "✅ DB is up - running migrations..."
python create_db.py

echo "🚀 Starting app..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
