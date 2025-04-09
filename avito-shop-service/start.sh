#!/bin/bash

# Run migrations
alembic upgrade head

# Start the application
exec uvicorn app:app --host 0.0.0.0 --port 8800
